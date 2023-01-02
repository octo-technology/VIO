Feature: The client request metadata and binaries

  Scenario: The Client reads all items metadata
    Given the app is up and running
    When the client requests the items metadata list
    Then the client receives the items metadata list

  Scenario: The Client reads one specific item metadata
    Given the app is up and running
    And item 'item_id' is stored
    When the item 'item_id' metadata is requested
    Then the item 'item_id' metadata is read
      | serial_number | category | nb_cameras |
      | serial_number | category | 1          |

  Scenario: The Client reads one specific item picture
    Given the app is up and running
    Given item 'item_id' is stored
    When one item 'item_id' binary from camera 'camera_id3' is requested
    Then one item 'item_id' binary from camera 'camera_id3' is read
