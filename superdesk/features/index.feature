Feature: Test superdesk web app index

    Scenario: Get Index With Top 3 articles
        Given Fixture "packageitem_complete.json"
        When I send GET request to "/"
        Then I get response code 200
        And I see 1 section with title "UK"
        And I see 3 articles
