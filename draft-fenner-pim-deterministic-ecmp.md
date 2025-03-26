---
title: "Deterministic Upstream Neighbor Selection for PIM Joins"
abbrev: "PIM Upstream Deterministic ECMP"
category: info

docname: draft-fenner-pim-deterministic-ecmp-latest
submissiontype: IETF  # also: "independent", "editorial", "IAB", or "IRTF"
number:
date:
consensus: true
pi:
 - comments: no
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
    email: "fenner@fenron.com"
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

In a densely interconnected network, there may be many equal-cost
paths to a given source or RP.  RFC7761 is silent on the issue of
how to choose among these, just indicating that RPF_interface(S)
and RPF_interface(RP) have a single answer. If different leaf routers
make different choices, then traffic can flow over extra paths.

This document introduces two mechanisms: one for two-tier networks
and one for arbitrary multi-tier networks, to allow routers to make the same
decision of which neighbor to use in an ECMP scenario.  This eliminates
undesired redundant traffic flow.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Hash Algorithm

In this document, the hash algorithm used is Bob Jenkin's one-at-a-time hash.
This is a very high quality, but fast hash function.
[Wikipedia](https://en.wikipedia.org/wiki/Jenkins_hash_function#one_at_a_time)
has one description of the algorithm.  This hash function is defined on sequences of
octets; it is performed across all of the addresses given in network byte order.

Pseudocode like `hash( address1, address2, address3 )` conceptually
lays out these addresses adjacent to each other in memory in network
byte order, and performs a single hash operation across all 12 octets.

{::comment}
protocol -b 24 -n address1:8,address2:8,address3:8
and then edited with s/-+-/---/g
{:/comment}
~~~~
+---+---+---+---+---+---+---+---+---+---+---+---+
|    address1   |    address2   |    address3   |
+---+---+---+---+---+---+---+---+---+---+---+---+
~~~~

Similarly, when there are two IPv6 addresses and a router ID, we
conceptually lay these out identically, simply with larger addresses,
and perform the hash operation across all 36 octets.

{::comment}
protocol 'address1:32,address2:32,router ID:8'
and then edited with s/-+-/---/g
{:/comment}
~~~~
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|                            address1                           |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|                            address2                           |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   router ID   |
+---+---+---+---+
~~~~

When the hash involves a color, that 32-bit value in network byte order
takes the place of the 32-bit router ID.

# Deterministic Selection by Router-ID {#routerid}

We use the {{RFC6395}} Hello Option to allow multiple routers to hash a given (S,G)
join to the same RPF neighbor.  The procedure consists of two phases: first,
we compute `hash( S, G, routerId )` for each eligible RPF neighbor, and select the
highest hash value among this list.  If there are multiple entries with the highest
hash value, we re-hash among this sub-list using `hash( S, G, local-information )`,
and use the highest single resulting hash value.  If multiple hops still hash to
the same value, we simply take the first one in the list.  This results in no
coordination between nodes, since each node may have a different order for the
list.

The `local-information` is a value local to the router that can be influenced by the
deployment to have the same result between multiple peers - e.g., it could be an
interface name, and the deployment on multiple routers uses the same interface to
connect to the same peer.  It could also be a locally-configured value on each
interface, which results in higher configuration overhead but more deployment
flexibility.

~~~
viaMultipathRouterId( source, group, vias )
    bestHash = 0
    bestVias = []
    for via in vias:
        routerId = getRouterId( via )
        curHash = hash( source, group, routerId )
        if curHash > bestHash:
            bestVia = [ via ]
            bestHash = curHash
        else if curHash == bestHash:
            bestVia.append( via )
    bestHash = 0
    if len( bestVia ) == 1:
        return bestVia[0]
    for via in bestVia:
        curHash = hash( source, group, local-information )
        if curHash > bestHash:
            bestVia = via

    return bestVia
~~~
{: #RouterIdPseudocode title='Pseudocode for Deterministic Hashing based on Router ID'}
[^2]

[^2]: pseudocode format TBD

# Hello Option to Exchange Color

We describe a Hello Option to exchange "Color", an abstract notion
of grouping of nodes.  For example, in a 3-tier network, the routers in
the middle tier could be colored by the spine to which they connect in
the top tier. In this way, the color value presented to the leaf routers
by the middle tier is a proxy for the routers in the top tier.

This Hello option should only be advertised "downwards" towards the
lower levels of the tree.

## Color Hello Option Message Format

The PIM Hello Option used to exchange Color values is shown below.

{::comment}
protocol 'Type = TBD:16,Length = 4:16,Color:32'
{:/comment}
~~~~
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Type = TBD          |           Length = 4          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Color                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
~~~~
{: #ColorHelloOption title='Color Hello Option'}

Type: TBD (see {{iana}} and {{arista-compatibility}})

Length: In bytes for the value part of the Type/Length/Value encoding.
The Color will be 4 bytes long.

Color: The color value being advertised by this router.

# Deterministic Selection by Color

TBD: If not all neighbors advertise color, do we pick from the subset
that do, or we fall back to {{routerid}}?

We use the above Hello Option to add an initial round of hashing,
falling back to the algorithm in {{RouterIdPseudocode}} to break ties.
With this mechanism, the first round is to calculate
`hash( S, G, color )` for each eligible RPF neighbor, and select
the highest hash value among this list.  If there are multiple entries
with the highest hash value, we re-hash among this sub-list
with `viaMultipathRouterId` defined above.

~~~
viaMultipathColor( source, group, vias )
    bestHash = 0
    bestVias = []
    for via in vias:
        color = getNeighborColor( via )
        curHash = hash( source, group, color )
        if curHash > bestHash:
            bestVia = [ via ]
            bestHash = curHash
        else if curHash == bestHash:
            bestVia.append( via )
    bestHash = 0
    if len( bestVia ) == 1:
        return bestVia[0]
    return viaMultipathRouterId( source, group, bestVia )
~~~
{: #ColorPseudocode title='Pseudocode for Deterministic Hashing based on Color'}
[^3]

[^3]: pseudocode format TBD

# Security Considerations

TODO Security


# IANA Considerations {#iana}

IANA is requested to allocate a value from the PIM-Hello Options
registry as shown:

| Value | Length | Name  | Reference
| TBD   | 4      | Color | This Document

--- back

# Arista Networks Compatibility {#arista-compatibility}

This non-normative appendix describes the Arista Proprietary
Color option, for the benefit of compatibility with the
deployed base.  A standards-compliant implementation
SHOULD NOT emit or parse these options by default, but MAY
have a configuration option to emit and parse these options
on a given interface for interoperability.

A pair of PIM Hello options is required for compatibility
with the deployed base of Arista EOS.  Both types are allocated
from the "Private Use" reserved range.  The first option, with
type 65001, only serves to indicate with a "magic number" that
the type 65002 option is indeed the Arista Proprietary Color
option (as opposed to some other Private Use).

These option formats are shown below.

{::comment}
protocol 'Type = 65001:16,Length = 4:16,4028514875:32'
{:/comment}
~~~~
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Type = 65001         |           Length = 4          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           4028514875                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
~~~~
{: title='Enable Arista Proprietary Hello options'}

By including this PIM Hello option, with type 65001 and 32-bit
value 4028514875, you indicate that the rest of the PIM Hello
options that you are including are Arista-proprietary.

{::comment}
protocol 'Type = 65002:16,Length = 4:16,Color:32'
{:/comment}
~~~~
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Type = 65002         |           Length = 4          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Color                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
~~~~
{: title='Arista Proprietary Color option'}

The Arista Proprietary Color option is identical to the
option described in figure {{ColorHelloOption}}, except for
the Type field.  It is only recognized if the Arista Proprietary
Hello options are enabled by the option above.

## Arista Color Hash Algorithm

The Arista-compatible hash algorithm stores the color in little-endian
byte order when hashing.

{::comment}
protocol -b 36 -n 'address1:12,address2:12,color(little-endian):12'
and then edited with s/-+-+-/-----/g
{:/comment}
~~~~
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|        address1       |        address2       |  color(little-endian) |
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
~~~~

When all routers in a set of vias are exchanging color information via
the RFC-specified COLOR option, they MUST use the standard hash with
the color in network byte order.
When at least one router in a set of vias is exchanging color information via the Arista Proprietary
Color option, they MUST use the Arista-compatible hash algorithm
to compare colors.

# Sample Hash Values

Hashing with Router-ID:

~~~~
hash( 192.0.0.2, 224.1.1.1, 10.0.0.1 ) = 3391492512
hash( 192.0.0.2, 224.1.1.1, 10.0.0.2 ) = 3391493567
hash( 192.0.0.2, 224.1.1.1, 10.0.0.3 ) = 3391498574
~~~~
In this case, the neighbor with Router-ID 10.0.0.3 would
be chosen.

Hashing with Color, Arista-compatible:

~~~~
hash( 192.0.0.2, 224.1.1.1, 10 ) = 3391495569
hash( 192.0.0.2, 224.1.1.1, 20 ) = 797801633
hash( 192.0.0.2, 224.1.1.1, 30 ) = 2218733534
~~~~
In this case, the neighbor with color 10 would be chosen.

Hashing with Color, RFC-compatible:

~~~~
hash( 192.0.0.2, 224.1.1.1, 10 ) = 4240030715
hash( 192.0.0.2, 224.1.1.1, 20 ) = 4240032301
hash( 192.0.0.2, 224.1.1.1, 30 ) = 4240042647
~~~~
In this case, the neighbor with color 30 would be chosen.


# Acknowledgments
{:numbered="false"}

TODO acknowledge.
