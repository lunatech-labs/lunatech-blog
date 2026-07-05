package com.lunatech.blog;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.logging.Logger;

import io.quarkiverse.roq.frontmatter.runtime.model.DocumentPage;
import io.quarkiverse.roq.frontmatter.runtime.model.Site;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import jakarta.ws.rs.WebApplicationException;

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

    @RestClient
    GitHubUsers gitHub;

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
        String authorization = token.map(t -> "Bearer " + t).orElse(null);
        for (String handle : handles) {
            names.put(handle, fetchName(handle, authorization));
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

    private String fetchName(String handle, String authorization) {
        try {
            String name = gitHub.user(handle, authorization).name();
            if (name != null && !name.isBlank()) {
                return name;
            }
        } catch (WebApplicationException e) {
            LOG.warnf("GitHub users API returned %d for '%s'; keeping the handle as byline",
                    e.getResponse().getStatus(), handle);
        } catch (Exception e) {
            LOG.warnf("GitHub user lookup failed for '%s' (%s); keeping the handle as byline",
                    handle, e.toString());
        }
        return handle;
    }
}
