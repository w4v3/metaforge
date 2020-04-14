syntax keyword mfgKeyWords em asc desc wd lft rt

syntax match mfgEntryDelim "^\*"
syntax match mfgEntryDelim "^+"
syntax match mfgEntryDelim "^/"
syntax match mfgEntryColon ":" contained
syntax match mfgGlyph "^/\S\+$" contains=mfgEntryDelim

syntax region mfgEntryKey start=/^*\|+/ end="\n" oneline contains=mfgEntryDelim,mfgEntryValue,mfgKeyWords
syntax region mfgEntryValue start=":" end="$" oneline contained contains=mfgEntryColon,mfgKeyWords
syntax region mfgEmph matchgroup=Ignore start="\~" end="\~" concealends contains=Ignore

highlight link mfgKeyWords Special
highlight link mfgEntryDelim Operator
highlight link mfgEntryKey Identifier
highlight link mfgEntryColon mfgEntryKey
highlight link mfgEntryValue String
highlight link mfgGlyph Type
highlight link mfgEmph Title

set conceallevel=2
