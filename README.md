# IMAGE SWARM

`image-swarm` is a utility service to update Docker containers in a Swarm.

ENVIRONMENT VARIABLES

| NAME                  | DEFAULT   | DESCRIPTION                               |
| :---                  | :------   | :-----------                              |
| INTERVAL              | 300       | Interval for checking images in seconds   |
| LOG_LEVEL             | INFO      | Python log level                          |
| AWS_ACCESS_KEY_ID     | None      | AWS key                                   |
| AWS_SECRET_ACCESS_KEY | None      | AWS key                                   |
| FILTER_LABELS         | false     | Whether or not to only check service with the `procedural.image-swarm.check=true` label |
| PRUNE                 | true      | Whether or not to prune images after a run |