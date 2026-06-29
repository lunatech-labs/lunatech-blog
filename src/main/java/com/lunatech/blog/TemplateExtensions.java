package com.lunatech.blog;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import io.quarkus.qute.TemplateExtension;
import io.vertx.core.json.JsonObject;

/**
 * Qute template extensions for the Lunatech blog theme.
 *
 * <p>The AsciiDoc plugin stores a post's {@code :tags:} attribute as a raw
 * bracketed string (e.g. {@code "[java, jvm, scala]"}) under
 * {@code page.data.attributes}. This exposes it to templates as a clean,
 * de-duplicated, lower-cased list via {@code page.data.attributes.tagList}.
 */
@TemplateExtension
public class TemplateExtensions {

    /**
     * Parse the bracketed AsciiDoc {@code tags} attribute into a list of tags.
     * Returns an empty list when the attribute is absent.
     */
    static List<String> tagList(JsonObject attributes) {
        if (attributes == null) {
            return List.of();
        }
        String raw = attributes.getString("tags", null);
        if (raw == null || raw.isBlank()) {
            return List.of();
        }
        String body = raw.trim();
        if (body.startsWith("[")) {
            body = body.substring(1);
        }
        if (body.endsWith("]")) {
            body = body.substring(0, body.length() - 1);
        }
        Set<String> tags = new LinkedHashSet<>();
        for (String part : body.split(",")) {
            String tag = part.trim().toLowerCase();
            if (!tag.isEmpty()) {
                tags.add(tag);
            }
        }
        return new ArrayList<>(tags);
    }
}
