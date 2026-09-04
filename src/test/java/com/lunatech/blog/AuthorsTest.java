package com.lunatech.blog;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

/**
 * Pure unit tests for the byline formatting; the GitHub lookup itself is
 * disabled in the test profile so nothing here touches the network.
 */
public class AuthorsTest {

    private final Authors authors = new Authors();

    @Test
    void unresolvedHandlePassesThrough() {
        assertEquals("hilton", authors.displayName("hilton"));
    }

    @Test
    void fullNamePassesThrough() {
        assertEquals("Michael Pentowski", authors.displayName("Michael Pentowski"));
    }

    @Test
    void multiAuthorValueIsCommaJoined() {
        assertEquals("njlbenn, eamelink, thinkmorestupidless",
                authors.displayName("njlbenn; eamelink; thinkmorestupidless"));
    }

    @Test
    void missingAuthorStaysNull() {
        assertNull(authors.displayName(null));
        assertNull(authors.displayName("  "));
    }
}
