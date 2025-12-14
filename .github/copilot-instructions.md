# Agent instructions

## Types of Activities

- **Features**: New functionality that adds value to the product.
- **Bugs**: Issues that need to be fixed to ensure the product works as intended
- **Chores**: Maintenance tasks that keep the project healthy, such as updating dependencies or improving documentation.
- **Spikes**: Research tasks to explore new technologies or approaches.

## git conventions

- Use descriptive commit messages.
- Follow the branching strategy (e.g., feature branches, bugfix branches).
- Keep commits small and focused.
- Regularly pull changes from the dev branch to avoid conflicts.
- Branch naming conventions:
  - Features: `feature/#<issue #>-short-description`
  - Bugs: `bugfix/#<issue #>-short-description`
  - Chores: `chore/#<issue #>-short-description`
  - Spikes: `spike/#<issue #>-short-description`
- Commit messages should follow:
  - <type>(#<issue #>): <short description>\n<detailed description (if necessary)>
  - Types: feat, fix, chore, spike
  - Example: `feat(#1234): add user authentication`
  - Include a '!' before the colon and "breaking change!" at the end of the first line to indicate breaking changes, e.g., `feat(#1234)!: change API endpoint`
