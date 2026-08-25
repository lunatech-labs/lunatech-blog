package com.lunatech.blog;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.Normalizer;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.jupiter.api.Test;

/**
 * A post's URL is its folder name run through Roq's slugifier (see the link
 * pattern in templates/layouts/post.html), which lowercases and replaces
 * accents, curly quotes and punctuation with '-'. A folder named outside that
 * alphabet is therefore served at a URL that does not match it, which silently
 * breaks anything deriving a post URL from disk.
 *
 * Requiring every folder to already be its own slug keeps the two identical.
 * scripts/RenamePosts.java applies the same rule and can fix offenders.
 *
 * This reads the filesystem only, so it deliberately does not boot the site.
 */
class PostFolderNameTest {

    private static final Path POSTS = Path.of("content", "posts");

    /** The slug alphabet: a yyyy-mm-dd prefix, then [a-z0-9] joined by single hyphens. */
    private static final Pattern SLUG =
            Pattern.compile("\\d{4}-\\d{2}-\\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*");

    @Test
    void postFolderNameIsItsOwnUrlSlug() throws IOException {
        List<String> offenders;
        try (Stream<Path> entries = Files.list(POSTS)) {
            offenders = entries.filter(Files::isDirectory)
                    .map(path -> path.getFileName().toString())
                    .filter(name -> !SLUG.matcher(name).matches())
                    .sorted()
                    .collect(Collectors.toList());
        }

        assertTrue(offenders.isEmpty(), () -> report(offenders));
    }

    /** Names the offenders and the slug each one should have. */
    private static String report(List<String> offenders) {
        StringBuilder message = new StringBuilder(offenders.size()
                + " post folder(s) are not a valid URL slug, so their folder name and"
                + " their URL disagree.\nRun 'java scripts/RenamePosts.java content/ --apply'"
                + " to rename them (URL-neutral):\n\n");
        for (String name : offenders) {
            message.append("  ").append(name).append("\n    -> ").append(slugify(name)).append("\n");
        }
        return message.toString();
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
}
