# Intake checklist

What an incoming request must settle before it becomes a Linear project.
`pm:intake` scores every item below. Each item's heading is also its section
heading in the project description, so a reader finds each answer where the
checklist put it.

## Scores

Every item gets exactly one:

- **answered**: the request says it. Cite the line.
- **inferable**: the request implies it. Write the inference as a claim the
  user can correct. It counts as answered once the user confirms it.
- **missing**: nothing in the request settles it. It becomes a question.

A requested solution scores nothing by itself. "Add a CSV export button" names
a solution; who needs the data, what goes wrong without it, and how anyone
would know it worked are all still missing.

## The items

In order. *Usually answered by* says where to take a missing item first: the
**requester** (a question for the reply the user sends) or the **user** (a question
asked in-session, or a fact read from the repo or Linear). For the user's own
idea, the user is the requester, so every *requester* item is asked in-session.

### Who

Who is asking, and who is affected. They are often different people.

- **Answered when:** the requester is named, and so is the person or role that
  hits the problem, with how often.
- **Inferable from:** the sender; the team, channel, or meeting it came from.
- **Usually answered by:** requester.
- **Ask:** "Who runs into this besides you, and how often?"

### Problem

The problem and the evidence for it, kept apart from the requested solution.

- **Answered when:** the request describes what goes wrong today and gives one
  concrete instance: an incident, a count, a quoted error, time lost.
- **Inferable from:** nothing. A request that states only a solution scores
  missing here, however detailed the solution is. Record that solution as the
  requester's proposal; it is a sketch for whoever builds this, never the spec.
- **Usually answered by:** requester.
- **Ask:** "What happened the last time this got in your way?"

### Done means

The success criteria: what the requester would check to call this finished.

- **Answered when:** there is an observable a third party could check without
  asking what was meant.
- **Inferable from:** the problem's evidence. The inverse of the failure is
  usually the finish line.
- **Usually answered by:** requester.
- **Ask:** "How will you know this worked?"

### Scope

The edges of the request, and its explicit non-goals.

- **Answered when:** at least one thing is named as in, and at least one as
  out.
- **Inferable from:** adjacent work the request did not mention. Propose each
  as a non-goal, by name, for the user to confirm.
- **Usually answered by:** either. The requester knows what they need; the user
  knows what sits next to it.
- **Ask:** "Is <a named adjacent thing> part of this, or separate?"

### Urgency

How soon, and the deadline if there is one.

- **Answered when:** there is a date and what happens on it, or an explicit "no
  deadline". "ASAP" and "soon" score missing.
- **Inferable from:** an event the request names (a launch, a renewal, an
  audit) whose date is known.
- **Usually answered by:** requester.
- **Ask:** "Is there a date this has to land by, and what happens if it slips?"

### Dependencies

Dependencies, data, and permissions the work needs.

- **Answered when:** the systems, data sources, access, and other teams the
  work touches are named, or the answer is "none".
- **Inferable from:** the repo and Linear: what the area already depends on,
  and which open tickets sit in the way.
- **Usually answered by:** user.
- **Ask:** "Does this need data or access we do not have today?"

### Open forks

The open design forks: places where two shapes both satisfy the request and
someone has to pick.

- **Answered when:** every fork is named, or there are none. Naming a fork is
  the whole score. The fork itself stays open through intake and decides the
  route afterwards: a request with open forks is charted, one without is
  sliced.
- **Inferable from:** a current decision that already closes the fork.
- **Usually answered by:** user.
- **Ask:** "If we built this two ways, which difference would the requester
  notice?"
