---
title: "Deterministic Upstream Neighbor Selection for PIM Joins"
abbrev: "PIM Upstream Deterministic ECMP"
category: info

docname: draft-fenner-pim-deterministic-ecmp-latest
submissiontype: IETF  # also: "independent", "editorial", "IAB", or "IRTF"
number:
date:
consensus: true
v: 3
area: "Routing"
workgroup: "Protocols for IP Multicast"
keyword:
 - ECMP
 - PIM Join
 - Data Center
venue:
  group: "Protocols for IP Multicast"
  type: "Working Group"
  mail: "pim@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/pim/"
  github: "fenner/pim-deterministic-ecmp"
  latest: "https://fenner.github.io/pim-deterministic-ecmp/draft-fenner-pim-deterministic-ecmp.html"

author:
 -
    fullname: "Bill Fenner"
    organization: Arista Networks, Inc.
    email: "fenner@gmail.com"
 -
    fullname: "Santosh Kumar"
    organization: Arista Networks, Inc.
    email: "skumar@arista.com"

normative:
  RFC6395:

informative:


--- abstract

In densely interconnected networks, a PIM node may have many choices
as to what upstream neighbor to send a JOIN message to, for a given
source and group.  This document describes a mechanism for multiple
nodes (e.g., leaf nodes in a data center) to pick the same upstream
node (e.g., spine node) to avoid redundant traffic flows.

--- middle

# Introduction

TODO Introduction


# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Hash Algorithm

In this document, the hash algorithm used is ...

# Deterministic Selection by Router-ID

We use the {{RFC6395}} Hello Option to ...

# Hello Option to Exchange Color

We describe a Hello Option to exchange "Color", an abstract notion
of grouping of ...

# Deterministic Selection by Color

We use the above Hello Option to ...

# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
