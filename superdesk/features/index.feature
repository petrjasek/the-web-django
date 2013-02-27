Feature: Test the superdesk web app renders index

    Scenario: Get Index
        Given I send GET request to "/"
        Then I get response code 200
        And I see title "Superdesk"
        And I see 1 article
