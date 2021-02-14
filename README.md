# Patreon post docker action

This action create post on your patreon page

## Inputs

### `login`

**Required** Patreon login 

### `password`

**Required** Password for patreon account. It is recommended to use [github secrets](https://docs.github.com/en/actions/reference/encrypted-secrets). 
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
```
