Feature: Test superdesk web app index

    Scenario: Get Index With Top 3 articles
        Given Fixture "items.json"
        When I send request to "/"
        Then I get response code 200
        And I see article links:
            | title                                              | link                                  |
            | Top Fed policymakers differ on QE3's effectiveness | tag:reuters.com,0000:newsml_BRE88C04U |

    Scenario: Get Item Page with full content
        Given Fixture "items.json"
        When I send request to "/article/tag:reuters.com,0000:newsml_BRE88C04U"
        Then I get response code 200
        And I see title "Top Fed policymakers differ on QE3's effectiveness" 
        And I see h1 "Top Fed policymakers differ on QE3's effectiveness" 
        And I see content with "ANN ARBOR, Michigan (Reuters) - Just days after the Federal Reserve launched"

    Scenario: Get non-existing item
        Given No fixture
        When I send request to "/article/tag:example.com,2008:TX-PAR:20080529:JYC99"
        Then I get response code 404

