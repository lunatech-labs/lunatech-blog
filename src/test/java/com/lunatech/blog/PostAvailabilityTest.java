package com.lunatech.blog;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.jupiter.api.Test;

import io.quarkiverse.roq.testing.RoqAndRoll;
import io.quarkus.test.junit.QuarkusTest;
import io.restassured.RestAssured;

/**
 * Requests every post bundle in content/posts/ and fails on any that does not
 * answer HTTP 200.
 *
 * The post list comes from disk rather than from the sitemap on purpose: a post
 * that fails to render never reaches the sitemap, so checking the sitemap alone
 * would never notice it was gone. Reading the directory instead means a post
 * cannot disappear silently.
 *
 * URLs are derived from the directory name, which is correct only while a post
 * directory is its own slug. PostFolderNameTest enforces exactly that, so these
 * two tests are a pair: break the naming rule and that test fails, not this one.
 */
@QuarkusTest
@RoqAndRoll
public class PostAvailabilityTest {

    private static final Path POSTS = Path.of("content", "posts");

    @Test
    void everyPostIsReachable() throws IOException {
        List<String> posts = postDirectoryNames();

        // Guard against a silent pass: an empty list would otherwise "succeed".
        assertFalse(posts.isEmpty(), "No post bundles found in " + POSTS.toAbsolutePath());

        List<String> failures = new ArrayList<>();
        for (String post : posts) {
            String path = "/posts/" + post + "/";
            int status = RestAssured.when().get(path).statusCode();
            if (status != 200) {
                failures.add("HTTP " + status + "  " + path);
            }
        }

        assertTrue(failures.isEmpty(), () -> failures.size() + " of " + posts.size()
                + " post(s) are not reachable:\n" + String.join("\n", failures));
    }

    private static List<String> postDirectoryNames() throws IOException {
        try (Stream<Path> entries = Files.list(POSTS)) {
            return entries.filter(Files::isDirectory)
                          .map(path -> path.getFileName().toString())
                          .sorted(Comparator.naturalOrder())
                          .collect(Collectors.toList());
        }
    }
}
