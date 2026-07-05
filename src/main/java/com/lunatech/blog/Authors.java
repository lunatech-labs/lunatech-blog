package com.lunatech.blog;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

import io.quarkiverse.roq.frontmatter.runtime.model.DocumentPage;
import io.quarkiverse.roq.frontmatter.runtime.model.Site;
import io.quarkus.runtime.StartupEvent;
import io.vertx.core.json.JsonObject;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

/**
 * Resolves post author values (GitHub handles) to profile display names via
 * the GitHub users API, the way the old blog engine did at runtime. All
 * lookups happen once at startup, before the generator renders any page, so
 * template rendering only reads the resolved map. A missing token, an unknown
 * user or an API failure falls back to the raw handle.
 *
 * CI passes the workflow token as GITHUB_TOKEN; without a token the
 * unauthenticated rate limit (60/h) covers only part of the ~80 distinct
 * handles, so local builds may show handles for the remainder.
 */
@Singleton
@Named("authors")
public class Authors {

    private static final Logger LOG = Logger.getLogger(Authors.class);

    private final Map<String, String> names = new ConcurrentHashMap<>();

    @ConfigProperty(name = "blog.author-lookup.enabled", defaultValue = "true")
    boolean enabled;

    @ConfigProperty(name = "github.token")
    Optional<String> token;

    void prefetch(@Observes StartupEvent event, Site site) {
        if (!enabled) {
            return;
        }
        Set<String> handles = new LinkedHashSet<>();
        for (DocumentPage post : site.collections().get("posts")) {
            String author = post.data().getString("author");
            if (author == null) {
                continue;
            }
            for (String part : author.split(";")) {
                String handle = part.trim();
                // values with a space are already full names, not handles
                if (!handle.isEmpty() && !handle.contains(" ")) {
                    handles.add(handle);
                }
            }
        }
        long start = System.currentTimeMillis();
        try (HttpClient http = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .followRedirects(HttpClient.Redirect.NORMAL)
                .build()) {
            for (String handle : handles) {
                names.put(handle, fetchName(http, handle));
            }
        }
        LOG.infof("Resolved %d author handle(s) via the GitHub users API in %d ms (token %s)",
                handles.size(), System.currentTimeMillis() - start,
                token.isPresent() ? "present" : "absent");
    }

    /**
     * The display name for a post's author value: a resolved GitHub profile
     * name, the raw value when unresolved, and a comma-joined list for
     * semicolon-separated multi-author values.
     */
    public String displayName(String author) {
        if (author == null || author.isBlank()) {
            return null;
        }
        return Arrays.stream(author.split(";"))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .map(h -> names.getOrDefault(h, h))
                .collect(Collectors.joining(", "));
    }

    private String fetchName(HttpClient http, String handle) {
        try {
            HttpRequest.Builder request = HttpRequest.newBuilder(URI.create("https://api.github.com/users/" + handle))
                    .header("Accept", "application/vnd.github+json")
                    .timeout(Duration.ofSeconds(10))
                    .GET();
            token.ifPresent(t -> request.header("Authorization", "Bearer " + t));
            HttpResponse<String> response = http.send(request.build(), HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                String name = new JsonObject(response.body()).getString("name");
                if (name != null && !name.isBlank()) {
                    return name;
                }
            } else {
                LOG.warnf("GitHub users API returned %d for '%s'; keeping the handle as byline",
                        response.statusCode(), handle);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOG.warnf("GitHub user lookup interrupted at '%s'; keeping the handle as byline", handle);
        } catch (Exception e) {
            LOG.warnf("GitHub user lookup failed for '%s' (%s); keeping the handle as byline",
                    handle, e.toString());
        }
        return handle;
    }
}
