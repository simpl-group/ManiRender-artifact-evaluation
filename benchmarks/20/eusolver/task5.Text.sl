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
			(Regex x StartRegex)
        ))

        ; terminals
		;Text
		(StartLength Int (2 3 4 5 6 7 8 9 10 11 12 13 14 16 19 24 26 28 30 34))
		(StartRegex String ("(NH|XL|DV)\d{3,3}"))
    )
)

; I/O
; +
(declare-var x7 OBJ)
(declare-var x32 OBJ)
(declare-var x51 OBJ)
; -
(declare-var x4 OBJ)
(declare-var x16 OBJ)
(declare-var x35 OBJ)
(declare-var x55 OBJ)
(declare-var x67 OBJ)

; facts
; userdefined args = {'Text': {'Regex': ['(NH|XL|DV)\\d{3,3}']}}
(constraint (= (Respect {"id": 7, "cls": "Text", "Context": "NH435", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) true))
(constraint (= (Respect {"id": 32, "cls": "Text", "Context": "DV491", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) true))
(constraint (= (Respect {"id": 51, "cls": "Text", "Context": "XL424", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) true))

(constraint (= (Respect {"id": 4, "cls": "Text", "Context": "UP886", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 16, "cls": "Text", "Context": "68822", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 35, "cls": "Text", "Context": "YM8", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 3}) false))
(constraint (= (Respect {"id": 55, "cls": "Text", "Context": "97C70", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 67, "cls": "Text", "Context": "UFY336", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 6}) false))

(check-synth)
