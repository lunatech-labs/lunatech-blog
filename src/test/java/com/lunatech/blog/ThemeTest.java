package com.lunatech.blog;

import static org.hamcrest.Matchers.containsString;

import org.junit.jupiter.api.Test;

import io.quarkiverse.roq.testing.RoqAndRoll;
import io.quarkus.test.junit.QuarkusTest;
import io.restassured.RestAssured;

/**
 * Smoke tests for the Lunatech theme: the home page renders the hero and post
 * cards, a post renders the themed article scaffold, and the tagging plugin
 * generates a /tags/:tag page for a known tag.
 */
@QuarkusTest
@RoqAndRoll
public class ThemeTest {

    @Test
    void homePageHasHeroAndCards() {
        RestAssured.when().get("/")
                .then().statusCode(200)
                .body(containsString("cover__title"))
                .body(containsString("class=\"card\""));
    }

    @Test
    void postRendersThemedArticle() {
        RestAssured.when().get("/posts/2024-11-29-jvm-vs-jvm/")
                .then().statusCode(200)
                .body(containsString("post__title"))
                .body(containsString("min read"));
    }

    @Test
    void tagPageIsGenerated() {
        RestAssured.when().get("/tags/java/")
                .then().statusCode(200)
                .body(containsString("Posts tagged"))
                .body(containsString("class=\"card\""));
    }
}
