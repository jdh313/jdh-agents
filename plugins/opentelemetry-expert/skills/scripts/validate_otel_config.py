#!/usr/bin/env python3
"""
Validate OpenTelemetry Collector YAML configuration.

Usage:
    python validate_otel_config.py <config.yaml>
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate OTel collector config and return list of issues."""
    issues = []

    # Check required top-level sections
    required_sections = ["receivers", "exporters", "service"]
    for section in required_sections:
        if section not in config:
            issues.append(f"Missing required section: '{section}'")

    # Validate receivers
    if "receivers" in config:
        receivers = config["receivers"]
        if not receivers:
            issues.append("'receivers' section is empty")

        # Check for OTLP receiver (most common)
        if "otlp" in receivers:
            otlp = receivers["otlp"]
            if "protocols" not in otlp:
                issues.append("OTLP receiver missing 'protocols' configuration")
            else:
                protocols = otlp["protocols"]
                if "grpc" not in protocols and "http" not in protocols:
                    issues.append("OTLP receiver should have at least 'grpc' or 'http' protocol")

                # Check grpc endpoint
                if "grpc" in protocols:
                    grpc = protocols["grpc"]
                    if "endpoint" in grpc:
                        endpoint = grpc["endpoint"]
                        if endpoint.startswith("localhost:"):
                            issues.append(
                                f"OTLP gRPC endpoint '{endpoint}' uses 'localhost' - "
                                "should use '0.0.0.0:' to accept external connections"
                            )

    # Validate exporters
    if "exporters" in config:
        exporters = config["exporters"]
        if not exporters:
            issues.append("'exporters' section is empty")

    # Validate service pipelines
    if "service" in config:
        service = config["service"]
        if "pipelines" not in service:
            issues.append("'service' section missing 'pipelines'")
        else:
            pipelines = service["pipelines"]
            if not pipelines:
                issues.append("'service.pipelines' is empty")

            for pipeline_name, pipeline in pipelines.items():
                # Check receivers
                if "receivers" not in pipeline:
                    issues.append(f"Pipeline '{pipeline_name}' missing 'receivers'")
                else:
                    for receiver in pipeline["receivers"]:
                        if receiver not in config.get("receivers", {}):
                            issues.append(
                                f"Pipeline '{pipeline_name}' references undefined receiver '{receiver}'"
                            )

                # Check exporters
                if "exporters" not in pipeline:
                    issues.append(f"Pipeline '{pipeline_name}' missing 'exporters'")
                else:
                    for exporter in pipeline["exporters"]:
                        if exporter not in config.get("exporters", {}):
                            issues.append(
                                f"Pipeline '{pipeline_name}' references undefined exporter '{exporter}'"
                            )

                # Check processors (optional but recommended)
                if "processors" in pipeline:
                    for processor in pipeline["processors"]:
                        if processor not in config.get("processors", {}):
                            issues.append(
                                f"Pipeline '{pipeline_name}' references undefined processor '{processor}'"
                            )

    # Validate processors (if present)
    if "processors" in config:
        processors = config["processors"]

        # Warn if memory_limiter is missing (recommended)
        if "memory_limiter" not in processors:
            issues.append("WARNING: 'memory_limiter' processor not configured (recommended for production)")

        # Warn if batch is missing (recommended)
        if "batch" not in processors:
            issues.append("WARNING: 'batch' processor not configured (recommended for efficiency)")

        # Check memory_limiter configuration
        if "memory_limiter" in processors:
            memory_limiter = processors["memory_limiter"]
            if "limit_mib" not in memory_limiter:
                issues.append("'memory_limiter' processor missing 'limit_mib' configuration")

    return issues


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_otel_config.py <config.yaml>")
        sys.exit(1)

    config_path = Path(sys.argv[1])

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML syntax in {config_path}")
        print(e)
        sys.exit(1)

    issues = validate_config(config)

    if not issues:
        print(f"✅ Configuration is valid: {config_path}")
        sys.exit(0)
    else:
        print(f"❌ Configuration has {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
