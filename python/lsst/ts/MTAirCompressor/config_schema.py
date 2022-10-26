__all__ = ["CONFIG_SCHEMA"]

import yaml


CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_MTAirCompressor/blob/master/schema/aircompressor.yaml
# title must end with one or more spaces followed by the schema version, which must begin with "v"
title: AirCompressor v1
description: Schema for MT Air Compressor CSC configuration files
type: object
properties:
  instances:
    type: array
    description: Configuration for each compressor.
    minItem: 1
    items:
      type: object
      properties:
        sal_index:
          description: Index of the component
          type: integer
          minimum: 1
        grace_period:
          description: >-
            Number of seconds for which connection can be lost without failing.
          type: number
          default: 5
        host:
          description: Compressor controller TCPModbus gateway hostname.
          type: string
        port:
          description: Compressor controller TCPModbus gateway port.
          type: integer
          default: 502
        unit:
          description: Modbus unit number / address.
          type: integer
          default: 0
        required:
          - sal_index
        additionalProperties: false
required:
  - instances
additionalProperties: false
"""
)
