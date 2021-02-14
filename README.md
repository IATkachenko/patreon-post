# Patreon post docker action

This action create post on your patreon page
## Requirements

You **must** have proxy server with static IP, because patreon require to confirm auth attempt from new device.

## Inputs

### `login`

**Required** Patreon login 

### `password`

**Required** Password for patreon account. It is recommended to use [github secrets](https://docs.github.com/en/actions/reference/encrypted-secrets). 

### `body`

**Optional** Post body. Must be set if action is used not on "release" trigger

## Outputs

### `url`

Post url

## Example usage
```yaml
name: patreon post
on:
  release:
    types: 
      - 'published'
jobs:
  create_post:
    runs-on: ubuntu-latest
    name: patreon post
    steps:
      - name: post        
        uses: IATkachenko/patreon-post@v1
        with:
          login: 'IATkachenko'
          password: ${{ secrets.SuperSecretPatreonPassword }} 
        env:
          HTTPS_PROXY: ${{ secrets.HTTPS_PROXY }}
```
