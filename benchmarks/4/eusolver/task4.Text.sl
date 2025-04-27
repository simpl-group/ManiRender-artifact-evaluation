(set-logic OBJ)

; ∀ x ∈ POS. Respect(x) = true
; ∀ x ∈ NEG. Respect(x) = false
(synth-fun Respect ((x OBJ)) Bool
    (
        (Start Bool (
            ; Or/And/Not
            (Or Start Start)
            (And Start Start)
            (Not Start)

            ; userdefined functions
			; Text
			(Empty x)
			(PureNumber x)
			(PureAlphabet x)
			(LengthLess x StartLength)
			(LengthGreater x StartLength)
			(LengthEq x StartLength)
			(In x StartIn)
        ))

        ; terminals
		;Text
		(StartLength Int (3 5 7 8 9 10 11 12 13))
		(StartIn String ("COMPUTERS" "TURNS"))
    )
)

; I/O
; +
(declare-var x1 OBJ)
(declare-var x4 OBJ)
(declare-var x5 OBJ)
(declare-var x11 OBJ)
; -
(declare-var x8 OBJ)
(declare-var x9 OBJ)

; facts
; userdefined args = {'Text': {'In': ['COMPUTERS', 'TURNS']}}
(constraint (= (Respect {"id": 1, "cls": "Text", "Context": "UARE GALLERY", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 12}) true))
(constraint (= (Respect {"id": 4, "cls": "Text", "Context": "Fle", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 3}) true))
(constraint (= (Respect {"id": 5, "cls": "Text", "Context": "VISTAMEDIA", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 10}) true))
(constraint (= (Respect {"id": 11, "cls": "Text", "Context": "RCODE", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 5}) true))

(constraint (= (Respect {"id": 8, "cls": "Text", "Context": "COMPUTERS", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 9}) false))
(constraint (= (Respect {"id": 9, "cls": "Text", "Context": "NO TURNS", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 8}) false))

(check-synth)
