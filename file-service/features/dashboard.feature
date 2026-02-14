Feature: User Dashboard
    As a User
    I want to use the user dashboard
    So that I can perform basic file management operations

    Scenario: Authorised access
        Given I am logged in to my account
        When I access the user dashboard
        Then the response should contains dashboard data and HTTP status of 200.

    Scenario: Unauthorised access
        Given I am not logged in to my account
        When I access the user dashboard
        Then the respond should return HTTP status of 401 and JSON error.

    Scenario: Data isolation
        Given User A exists 
        And User B exists
        And User A has 1 file
        And User B has 1 file
        And I am authenticated as User A
        When I request /dashboard
        Then the response contains only User A's file 
        And does not contain User B's file.

    Scenario: Empty state
        Given I am logged in to my account and I have never upload a file or have deleted all my uploaded files in the database
        When I access the user dashboard
        Then the file array in the returned JSON list should be empty