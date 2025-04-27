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
			(StartsWith x StartStartsWith)
        ))

        ; terminals
		;Text
		(StartLength Int (2 3 4 5 6 7 8 9 10 11 12 13 14 16 19 24 26 28 30 34))
		(StartStartsWith String ("0" "1" "2" "3" "4" "5" "6" "7" "8" "9"))
    )
)

; I/O
; +
(declare-var x94 OBJ)
(declare-var x95 OBJ)
; -
(declare-var x16 OBJ)
(declare-var x36 OBJ)
(declare-var x61 OBJ)
(declare-var x129 OBJ)
(declare-var x131 OBJ)
(declare-var x143 OBJ)

; facts
; userdefined args = {'Text': {'StartsWith': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']}}
(constraint (= (Respect {"id": 94, "cls": "Text", "Context": "86498", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) true))
(constraint (= (Respect {"id": 95, "cls": "Text", "Context": "86498", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) true))

(constraint (= (Respect {"id": 16, "cls": "Text", "Context": "68822", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 36, "cls": "Text", "Context": "14163", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 61, "cls": "Text", "Context": "XL547", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 5}) false))
(constraint (= (Respect {"id": 129, "cls": "Text", "Context": "222698", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 6}) false))
(constraint (= (Respect {"id": 131, "cls": "Text", "Context": "3627", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 4}) false))
(constraint (= (Respect {"id": 143, "cls": "Text", "Context": "21", "Empty": False, "PureNumber": True, "PureAlphabet": False, "Length": 2}) false))

(check-synth)
