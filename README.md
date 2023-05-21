# `salt-ssh` action - simple `salt-ssh` runner for GitHub Actions

`salt-ssh-action` speeds up and simplifies using `salt-ssh` inside your GitHub
Action workflows by downloading a pre-built docker image for speedy builds.
This has the benefit of being faster that manually installing `salt` and its
dependencies on every workflow run.

## Usage

Using this workflow is as simple as:

```yaml
jobs:
  some_job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amplium/salt-ssh-action@master
```

The action defaults to the following `master` config file, making the need for
extra configuration minimal.

```yaml
file_roots:
  base:
    - <repository_root>/salt

pillar_roots:
  base:
    - <repository_root>/pillar
```

Although, this is sufficient for a lot of use-cases, all `salt-ssh` options
are available as inputs to the action and you can pretty much do anything you
want.

```yaml
- uses: amplium/salt-ssh-action@master
  with:
    target: database
    function: mysql.query
    arguments: saltenv=production "DROP TABLE users;"
    config-dir: somewhere/in/your/repository
    private-key: a-base64-encoded-key
```

## Advanced usage

If the simple usage above doesn't scratch your itch and you require more
control, you can simply run your workflow inside the container with `salt-ssh`
pre-installed so you shave off those precious CI seconds.

```yaml
jobs:
  some-job:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/amplium/salt-ssh-action
    steps:
      - run: salt-ssh <your options here>
```

## Inputs

These inputs are action-specific.

- target: Specify the targeted minions. Default: `'*'`.
- function: The function to apply to the targeted minions. Default: `state.highstate`.
- arguments: Additional arguments to pass to the salt-ssh command.
- private-key: The base64-encoded private key to use for connecting to the minions.
- known-hosts: The base64-encoded known_hosts file contents to setup before calling salt-ssh.
- known-hosts-file: The known_hosts file to setup before calling salt-ssh.

The rest are passed to `salt-ssh`.

- saltfile: Specify the path to a Saltfile. If not passed, one will be searched for in the current working directory.
- config-dir: Pass in an alternative configuration directory. Default: `/etc/salt`.
- jid: Pass a JID to be used instead of generating one.
- hard-crash: Raise any original exception rather than exiting gracefully. Default: False.
- no-parse: Comma-separated list of named CLI arguments (i.e. argname=value) which should not be parsed as Python data types
- raw-shell: Don't execute a salt routine on the targets, execute a raw shell command.
- roster: Define which roster system to use, this defines if a database backend, scanner, or custom roster system is used. Default: `flat`.
- roster-file: Define an alternative location for the default roster file location. The default roster file is called roster and is found in the same directory as the master config file.
- refresh-cache: Force a refresh of the master side data cache of the target's data. This is needed if a target's grains have been changed and the auto refresh timeframe has not been reached.
- max-procs: Set the number of concurrent minions to communicate with. This value defines how many processes are opened up at a time to manage connections, the more running processes the faster communication should be. Default: 25.
- extra-filerefs: Pass in extra files to include in the state tarball.
- min-extra-modules: One or comma-separated list of extra Python modules to be included into Minimal Salt.
- thin-extra-modules: One or comma-separated list of extra Python modules to be included into Thin Salt.
- verbose: Turn on command verbosity, display jid.
- static: Return the data from minions as a group after they all return.
- wipe: Remove the deployment of the salt files when done executing.
- rand-thin-dir: Select a random temp dir to deploy on the remote system. The dir will be cleaned after the execution.
- regen-thin: Trigger a thin tarball regeneration. This is needed if custom grains/modules/states have been added or updated.
- python2-bin: Path to a python2 binary which has salt installed.
- python3-bin: Path to a python3 binary which has salt installed.
- pre-flight: Run the defined ssh_pre_flight script in the roster
- hosts: List all known hosts to currently visible or other specified rosters
- pcre: Instead of using shell globs to evaluate the target servers, use pcre regular expressions.
- list: Instead of using shell globs to evaluate the target servers, take a comma or whitespace delimited list of servers.
- grain: Instead of using shell globs to evaluate the target use a grain value to identify targets, the syntax for the target is the grain key followed by a globexpression: `os:Arch*`.
- grain-pcre: Instead of using shell globs to evaluate the target use a grain value to identify targets, the syntax for the target is the grain key followed by a pcre regular expression: `os:Arch.*`.
- nodegroup: Instead of using shell globs to evaluate the target use one of the predefined nodegroups to identify a list of targets.
- range: Instead of using shell globs to evaluate the target use a range expression to identify targets. Range expressions look like %cluster.
- delimiter: Change the default delimiter for matching in multi-level data structures. Default: `:`.
- output: Print the output from the `salt-ssh` command using the specified outputter.
- output-indent: Print the output indented by the provided value in spaces. Negative values disables indentation. Only applicable in outputters that support indentation.
- output-file: Write the output to the specified file.
- output-file-append: Append the output to the specified file.
- no-color: Disable all colored output.
- force-color: Force colored output.
- state-output: Override the configured state_output value for minion output. One of `full`, `terse`, `mixed`, `changes` or `filter`. Default: `none`.
- state-verbose: Override the configured state_verbose value for minion output. Set to True or False. Default: none.
- remote-port-forwards: Setup remote port forwarding using the same syntax as with the -R parameter of ssh. A comma separated list of port forwarding definitions will be translated into multiple -R parameters.
- ssh-option: Equivalent to the -o ssh command option. Passes options to the SSH client in the format used in the client configuration file. Can be used multiple times.
- priv: Ssh private key file.
- priv-passwd: Passphrase for ssh private key file.
- ignore-host-keys: By default ssh host keys are honored and connections will ask for approval. Use this option to disable StrictHostKeyChecking.
- no-host-keys: Removes all host key checking functionality from SSH session.
- user: Set the default user to attempt to use when authenticating.
- passwd: Set the default password to attempt to use when authenticating.
- askpass: Interactively ask for the SSH password with no echo - avoids password in process args and stored in history.
- passwd: Set this flag to attempt to deploy the authorized ssh key with all minions. This combined with --passwd can make initial deployment of keys very fast and easy.
- identities-only: Use the only authentication identity files configured in the ssh_config files. See IdentitiesOnly flag in man ssh_config.
- sudo: Run command via sudo.
- update-roster: If hostname is not found in the roster, store the information into the default roster file (flat).
- scan-ports: Comma-separated list of ports to scan in the scan roster.
- scan-timeout: Scanning socket timeout for the scan roster.
- log-level: Console logging log level. One of `all`, `garbage`, `trace`, `debug`, `profile`, `info`, `warning`, `error`, `critical`, `quiet`. Default: `warning`.
- log-file: Log file path. Default: `/var/log/salt/ssh`.
- log-file-level: Logfile logging log level. One of `all`, `garbage`, `trace`, `debug`, `profile`, `info`, `warning`, `error`, `critical`, `quiet`. Default: `warning`.

## License

This GitHub Action is licensed under the [MIT License](./LICENSE)
