---
layout: datatype
title: TEXT!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 12
permalink: /docs/datatypes/text/
datatype: text!
summary: 'text string series of characters'
---

A textual string, such as `"abc"`.

*(Note: Historical Rebol called this STRING!  But due to other types in the
class of string such as the TAG! form like `<abc>`, Revolt uses the term
STRING! for the category of such types--not the most common instance of it.)*

## Dashed Strings

Text that is long, spans lines, or contains quotes can be written between
`-[` and `]-`:

```rebol
>> -[She said "hi" to me.]-
== -[She said "hi" to me.]-
```

Historical Rebol used braces for this, nesting by counting `{` and `}`.
That broke on unpaired braces, as in C code like `'}'`.  Braces are now
another list type called [FENCE!](/docs/datatypes/fence/) (peer to BLOCK! and
GROUP!), and the dashed form avoids the problem: a lone `]` or `{` inside
doesn't end anything.

```rebol
>> -[if (c = ']') { x[1] = 0; }]- = "if (c = ']') { x[1] = 0; }"
== \~okay~\  ; antiform (logic!)
```

### Nesting

A dashed string can contain another with the same number of dashes, as
long as the pairs match.  The inner `]-` closes the inner `-[`, not the
outer one:

```rebol
>> -[a -[b]- c]- = "a -[b]- c"
== \~okay~\  ; antiform (logic!)
```

The same goes for a nested pair with more dashes, which also matches up:

```rebol
>> -[a ---[b]--- c]- = "a ---[b]--- c"
== \~okay~\  ; antiform (logic!)
```

More dashes on the outside are only needed when the content has a closing
delimiter with no opening partner.  Then use more dashes than the content
does:

```rebol
>> --[an unpaired ]- inside]-- = "an unpaired ]- inside"
== \~okay~\  ; antiform (logic!)
```

See [Should Strings Nest Levels to Avoid Escaping?](https://rebol.metaeducation.com/t/should-strings-nest-levels-to-avoid-escaping/2311)
(2024) for the reasoning.
