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
        ))

        ; terminals
		;Text
		(StartLength Int (2 3 4 5 6 7 8 9 10 11 12 13 14 16 19 24 26 28 30 34))
    )
)

; I/O
; +
(declare-var x33 OBJ)
(declare-var x16 OBJ)
; -
(declare-var x7 OBJ)
(declare-var x8 OBJ)
(declare-var x48 OBJ)
(declare-var x61 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 33, "cls": "Text", "Context": "1330", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 4}) true))
(constraint (= (Respect {"id": 16, "cls": "Text", "Context": "68822", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) true))

(constraint (= (Respect {"id": 7, "cls": "Text", "Context": "NH435", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 8, "cls": "Text", "Context": "104781", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 6}) false))
(constraint (= (Respect {"id": 48, "cls": "Text", "Context": "814", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 3}) false))
(constraint (= (Respect {"id": 61, "cls": "Text", "Context": "XL547", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) false))

(check-synth)
