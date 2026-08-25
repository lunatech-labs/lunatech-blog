import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Renames post folders under <posts-directory>/posts/ to their own URL slug.
 *
 * A post's URL is its folder name run through Roq's slugifier (see the link
 * pattern in templates/layouts/post.html), which lowercases and replaces
 * accents, curly quotes and punctuation with '-'. A folder named outside that
 * alphabet is served at a URL that does not match it, so anything deriving a
 * URL from disk silently gets it wrong.
 *
 * Renaming a folder to its slug is URL-neutral: the slug of a slug is itself,
 * so the post keeps the exact URL it is already served at. Nothing needs a
 * redirect or an alias.
 *
 * Run with:
 *   java RenamePosts.java <posts-directory>            # dry run, prints the plan
 *   java RenamePosts.java <posts-directory> --apply    # performs the renames
 *
 * e.g. java scripts/RenamePosts.java content/ --apply
 *
 * PostFolderNameTest enforces the same rule; the two must agree.
 *
 * Exit code: 0 = nothing to do or renames applied, 1 = renames pending (dry
 * run) or a rename failed, 2 = bad usage.
 */
public class RenamePosts {

    /** The slug alphabet: a yyyy-mm-dd prefix, then [a-z0-9] joined by single hyphens. */
    private static final Pattern SLUG =
            Pattern.compile("\\d{4}-\\d{2}-\\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*");

    public static void main(String[] args) throws Exception {
        if (args.length < 1 || args.length > 2
                || (args.length == 2 && !args[1].equals("--apply"))) {
            System.err.println("Usage: java RenamePosts.java <posts-directory> [--apply]");
            System.exit(2);
        }

        boolean apply = args.length == 2;
        Path postsRoot = Path.of(args[0], "posts");
        if (!Files.isDirectory(postsRoot)) {
            System.err.println("Not a directory: " + postsRoot.toAbsolutePath());
            System.exit(2);
        }

        List<String> names = folderNames(postsRoot);
        Set<String> taken = new HashSet<>(names);

        List<Rename> plan = new ArrayList<>();
        for (String name : names) {
            if (SLUG.matcher(name).matches()) {
                continue;
            }
            String slug = slugify(name);
            // Guard the two properties that make this safe, rather than trusting them.
            if (!SLUG.matcher(slug).matches()) {
                System.err.println("Cannot derive a valid slug for: " + name);
                System.exit(1);
            }
            if (!slug.equals(name) && taken.contains(slug)) {
                System.err.println("Refusing to rename '" + name + "': '" + slug + "' already exists.");
                System.exit(1);
            }
            taken.add(slug);
            plan.add(new Rename(postsRoot, name, slug));
        }

        if (plan.isEmpty()) {
            System.out.println("All " + names.size() + " post folder(s) are already valid URL slugs.");
            System.exit(0);
        }

        for (Rename rename : plan) {
            for (String[] command : rename.commands()) {
                if (apply) {
                    run(command);
                } else {
                    System.out.println(String.join(" ", command));
                }
            }
        }

        if (apply) {
            System.out.println("Renamed " + plan.size() + " post folder(s).");
            System.exit(0);
        }
        System.out.println();
        System.out.println(plan.size() + " post folder(s) need renaming. Re-run with --apply.");
        System.exit(1);
    }

    private record Rename(Path root, String from, String to) {

        /**
         * git mv invocations for this rename. A case-only rename goes via a
         * temporary name because a case-insensitive filesystem (APFS, NTFS)
         * treats the source and target as the same path and would otherwise
         * fail or silently do nothing.
         */
        List<String[]> commands() {
            Path source = root.resolve(from);
            Path target = root.resolve(to);
            if (from.equalsIgnoreCase(to)) {
                Path temp = root.resolve(to + ".tmp");
                return List.of(
                        new String[] { "git", "mv", source.toString(), temp.toString() },
                        new String[] { "git", "mv", temp.toString(), target.toString() });
            }
            // Explicit type argument: a lone String[] would bind as varargs.
            return List.<String[]>of(new String[] { "git", "mv", source.toString(), target.toString() });
        }
    }

    private static void run(String[] command) throws IOException, InterruptedException {
        System.out.println(String.join(" ", command));
        Process process = new ProcessBuilder(command).inheritIO().start();
        int status = process.waitFor();
        if (status != 0) {
            System.err.println("Command failed with exit code " + status + ".");
            System.exit(1);
        }
    }

    /**
     * At least as aggressive as Roq's slugifier, so its output is always a valid
     * slug. Normalised to NFC first because a filesystem may hand back decomposed
     * accents ("e" plus a combining acute) where the repo stores a single 'é'.
     */
    private static String slugify(String name) {
        String nfc = Normalizer.normalize(name, Normalizer.Form.NFC).toLowerCase();
        return nfc.replaceAll("[^a-z0-9]+", "-").replaceAll("^-+|-+$", "");
    }

    private static List<String> folderNames(Path root) {
        try (Stream<Path> entries = Files.list(root)) {
            return entries.filter(Files::isDirectory)
                          .map(path -> path.getFileName().toString())
                          .sorted(Comparator.naturalOrder())
                          .collect(Collectors.toList());
        } catch (IOException e) {
            System.err.println("Cannot read " + root + ": " + e);
            System.exit(2);
            return List.of();
        }
    }
}
