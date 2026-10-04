# Sources behind the checks

Read when a finding needs a citation, or when the user disputes a check.

## Origin

Built from the lifeops vehicle Service/Health redesign (2026-10-03). Three research passes (hierarchy, copy, precedent) produced many recommendations; these checks are the ones that changed the outcome. The order is the main lesson: three rounds of hierarchy and copy fixes did not help, because the screen restated the Overview's answer. Splitting the tabs by time frame (Service = past records, Health = current condition) fixed it, and only then did the copy and density checks pay off. A triage-first layout (answer summary on top) was tried and rejected for the same reason: the summary already existed on a neighbour.

## Purpose and structure

- Progressive disclosure, show frequently needed things up front, at most two levels: https://www.nngroup.com/articles/progressive-disclosure/
- Users scan top-left first and read about 28% of words: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/ , https://www.nngroup.com/articles/website-reading/
- Few, Information Dashboard Design (2006): highlight the important item, arrange for comparison on the same scales, avoid excess detail (secondary summary): https://www.thedataschool.co.uk/anh-vu/are-you-making-these-13-dashboard-design-mistakes/
- Data table rhythm and row density: https://carbondesignsystem.com/components/data-table/usage/

## Copy

- Clarity, concision, character; every word serves a purpose: https://www.nngroup.com/articles/3-cs-microcopy/
- Table description is optional, column titles one or two words: https://carbondesignsystem.com/components/data-table/usage/
- Status needs a label, not color alone: https://carbondesignsystem.com/patterns/status-indicator-pattern/
- Verb plus noun actions: https://polaris.shopify.com/content/actionable-language
- Different destinations get different link text: https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html
- Gray placeholder-style text has poor contrast; keep load-bearing facts out of it: https://www.nngroup.com/articles/form-design-placeholders/

## Precedent (maintenance tracking)

- Fleetio separates service reminders, issues, and service history; issues resolve via a service entry: https://help.fleetio.com/en_US/issues-overview , https://help.fleetio.com/en_US/service-reminders-overview
- LubeLogger keeps service records and reminders on separate tabs: https://docs.lubelogger.com/Records/Reminders
