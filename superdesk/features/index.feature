Feature: Test superdesk web app index

    Scenario: Get Index With Top 3 articles
        Given Fixture "packageitem_complete.json"
        When I send request to "/"
        Then I get response code 200
        And I see 1 section with title "UK"
        And I see 3 articles
        And I see link to "/article/tag:example.com,2008:TX-PAR:20080529:JYC99"

    Scenario: Get Item Page with full content
        Given Fixture "packageitem_complete.json"
        When I send request to "/article/tag:example.com,2008:TX-PAR:20080529:JYC99"
        Then I get response code 200
        And I see title "Bank cuts interest rates to record low"

    Scenario: Get non-existing item
        Given No fixture
        When I send request to "/article/tag:example.com,2008:TX-PAR:20080529:JYC99"
        Then I get response code 404

