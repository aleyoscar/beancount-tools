
<a name="v2.1.0"></a>
## [v2.1.0](https://github.com/aleyoscar/beancount-importer/compare/v2.0.0...v2.1.0) (2026-01-16)

### Bug Fixes

* **app:** Sort pending transactions by date
* **app:** Style error
* **app:** Changed start-date and end-date command options
* **app:** Index print spacing when editing config. Fixes [#22](https://github.com/aleyoscar/beancount-importer/issues/22)
* **app:** Updated append_lines error message
* **app:** Edit config file before loading bills
* **app:** Changed [] to () in print_bills

### Code Refactoring

* **app:** Moved console to prompts.py. Closes [#23](https://github.com/aleyoscar/beancount-importer/issues/23)

### Features

* **app:** Set default debit account
* **app:** Pay unpaid bills. Closes [#20](https://github.com/aleyoscar/beancount-importer/issues/20)
* **app:** Show actual amount paid/due for current month. Closes [#19](https://github.com/aleyoscar/beancount-importer/issues/19)
* **app:** Payees completer. Closes [#18](https://github.com/aleyoscar/beancount-importer/issues/18)


<a name="v2.0.0"></a>
## [v2.0.0](https://github.com/aleyoscar/beancount-importer/compare/v1.1.0...v2.0.0) (2026-01-15)

### Bug Fixes

* **app:** Operating currency option typo

### Code Refactoring

* **app:** Moved console to prompts.py
* **app:** Move callbacks to prompts.py
* **core:** Rename project to beancount-tools/bean-tools

### Features

* **app:** Add missing bills and check for unpaid bills
* **app:** Added print bills helper
* **app:** Set dict or list default for get_json
* **app:** Added pending bills check tool
* **docs:** Add poetry build step


<a name="v1.1.0"></a>
## [v1.1.0](https://github.com/aleyoscar/beancount-importer/compare/v1.0.0...v1.1.0) (2026-01-08)

### Bug Fixes

* **app:** Update dependencies

### Features

* **app:** Show version info


<a name="v1.0.0"></a>
## [v1.0.0](https://github.com/aleyoscar/beancount-importer/compare/v0.1.1...v1.0.0) (2026-01-08)

### Bug Fixes

* **app:** Mismatched version info in __init__.py
* **app:** Test for empty response. Fixes [#14](https://github.com/aleyoscar/beancount-importer/issues/14)
* **app:** Move rec insertion. Fixes [#10](https://github.com/aleyoscar/beancount-importer/issues/10), closes [#11](https://github.com/aleyoscar/beancount-importer/issues/11) & closes [#13](https://github.com/aleyoscar/beancount-importer/issues/13)
* **docs:** Incorrect gen-chglog command

### Code Refactoring

* **app:** Reorganize code
* **app:** Moved Transactions class to helpers
* **app:** Moved ofx_pending and ofx_matches to helpers

### Features

* **app:** Parse SimpleFIN json files
* **app:** Added download and import commands
* **app:** Changed ofx to an option to prepare for simplefin
* **app:** Specify default flag for transactions. Closes [#12](https://github.com/aleyoscar/beancount-importer/issues/12)
* **app:** Evaluate basic expressions for float prompts. Closes [#8](https://github.com/aleyoscar/beancount-importer/issues/8)
* **app:** Color 'debit' and 'credit' text. Closes [#9](https://github.com/aleyoscar/beancount-importer/issues/9)
* **app:** Payee autocompletion grabs from ledger as well. Closes [#7](https://github.com/aleyoscar/beancount-importer/issues/7)
* **app:** Prompt for total. Closes [#4](https://github.com/aleyoscar/beancount-importer/issues/4) & closes [#5](https://github.com/aleyoscar/beancount-importer/issues/5)
* **app:** Switched number and answer colors for consistency
* **docs:** Added gen-chglog command for future use


<a name="v0.1.1"></a>
## [v0.1.1](https://github.com/aleyoscar/beancount-importer/compare/v0.1.0...v0.1.1) (2025-08-27)

### Bug Fixes

* **app:** Insert txn if matches not desired. Fixes [#1](https://github.com/aleyoscar/beancount-importer/issues/1)
* **app:** Remove autocomplete duplicates. Fixes [#2](https://github.com/aleyoscar/beancount-importer/issues/2)

### Code Refactoring

* **app:** Cleanup code

### Features

* **app:** Allow cancelling during insertion. Closes [#3](https://github.com/aleyoscar/beancount-importer/issues/3)


<a name="v0.1.0"></a>
## v0.1.0 (2025-08-26)

### Bug Fixes

* **app:** UTF-8 encoding
* **app:** Fix rec insertion
* **app:** Remove old account/id entry reconciliation method
* **app:** Only replace payee if inserting
* **app:** Update ledger info for every ofx transaction
* **app:** Write all files with LF line endings
* **app:** Insert newlines between transactions in buffer
* **app:** Typo in edit tags
* **app:** Performing regex fullmatch for validators
* **app:** Debit not negative
* **app:** Compare bean and ofx with absolute values
* **app:** Remove duplicate spaces
* **app:** Bad date reference
* **app:** Fix append to file
* **app:** Removed duplicate replace_payee calls

### Code Refactoring

* **app:** Reconcile based on postings
* **app:** Moved final log after buffer
* **app:** Consolidate validator options
* **app:** Replaced ofx data with account class
* **app:** Check resolve choice with first letter
* **app:** Moved theme into main

### Features

* **app:** Add counter
* **app:** Check postings for match when reconciling
* **app:** Add cli option shorthands. Add skip currency prompt
* **app:** Add completion for tags and links
* **app:** Edit transaction postings
* **app:** Edit transaction links
* **app:** Edit transaction tags
* **app:** Edit transaction narration
* **app:** Added final counts
* **app:** Edit transaction payee
* **app:** Edit transaction flag
* **app:** Edit transaction date
* **app:** Skeleton edit transaction
* **app:** Insert ofx information into beancount transaction
* **app:** Autocomplete beancount accounts
* **app:** Import transactions
* **app:** Reconcile transactions
* **app:** Iterate through pending txns and replace payee
* **app:** Add checks for empty lists
* **app:** Find pending transactions not in ledger
* **app:** Filter transactions by date
* **app:** Parse beancount ledger file
* **app:** Added currency print helper
* **app:** Parse ofx transactions
* **app:** Added promptsession and skeleton structure
* **app:** Validate ofx and ledger file paths
* **app:** Add prompt_toolkit dependency
* **core:** Add GNU GPL-3.0 license

