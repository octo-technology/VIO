resource "aws_iot_thing_group" "bapo-group" {
  name = "bapo-group"

  properties {
    description = "Bapo's thing group"
  }

  tags = {
    terraform = "true"
    context = "poc-greengrass-by-bapo"
  }
}

resource "aws_iot_thing" "bapo-raspberry" {
  name = "bapo-raspberry"
  thing_type_name = "edge-device"
}

resource "aws_iot_thing_group_membership" "bapo-thing-group" {
  thing_name       = "bapo-raspberry"
  thing_group_name = "bapo-group"

  override_dynamic_group = true
}