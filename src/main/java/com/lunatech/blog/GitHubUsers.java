package com.lunatech.blog;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.HeaderParam;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;

/**
 * The slice of the GitHub users API the blog needs: a login's profile, for the
 * display name. The base URL and timeouts live under
 * quarkus.rest-client.github in application.properties.
 */
@RegisterRestClient(configKey = "github")
public interface GitHubUsers {

    @GET
    @Path("/users/{handle}")
    GitHubUser user(@PathParam("handle") String handle, @HeaderParam("Authorization") String authorization);

    record GitHubUser(String name) {
    }
}
