# Changelog

## [1.3.3] - 2022-11-06

- Fix alternative type for `sem`

## [1.3.2] - 2022-10-20

- Use `contextlib.nullcontext` for dummy context manager instead of the buggy
  `Limitless`

## [1.3.1] - 2022-10-18

- Fix bug where semaphore was not being released when exceptions or early
  returns occured

## [1.3.0] - 2022-10-18

- Add option to control maximum number of concurrent downloads
- Refactor to use Python 3.10 typing syntax

## [1.2.0] - 2022-10-13

- Use asynchronous friendly version of `tqdm`
- Resize progress bars dynamically in response to screen size changes

## [1.1.0] - 2022-10-13

- Add cookie and user agent cli options

## [1.0.2] - 2022-10-10

- Loop over custom headers only once (`ketter.arguments`)
- Don't repeat code already in cli function (`ketter.__main__`)

## [1.0.1] - 2022-09-26

- Include description and readme in pyproject.toml
- Use banner image from cloud

## [1.0.0] - 2022-09-26

- First stable release
