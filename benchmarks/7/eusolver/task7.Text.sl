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
			(Regex x StartRegex)
			(In x StartIn)
        ))

        ; terminals
		;Text
		(StartLength Int (2 3 4 5 6 7 8 9 10 11 12 13 14 16 19 24 26 28 30 34))
		(StartStartsWith String ("NH" "XL" "DV"))
		(StartRegex String ("[a-zA-Z]{2,2}\d{3,3}"))
		(StartIn String ("BOOTED"))
    )
)

; I/O
; +
(declare-var x6 OBJ)
(declare-var x71 OBJ)
(declare-var x74 OBJ)
(declare-var x76 OBJ)
(declare-var x77 OBJ)
(declare-var x79 OBJ)
(declare-var x88 OBJ)
; -
(declare-var x70 OBJ)
(declare-var x72 OBJ)
(declare-var x73 OBJ)
(declare-var x83 OBJ)
(declare-var x85 OBJ)

; facts
; userdefined args = {'Text': {'StartsWith': ['NH', 'XL', 'DV'], 'Regex': ['[a-zA-Z]{2,2}\\d{3,3}'], 'In': ['BOOTED']}}
(constraint (= (Respect {"id": 6, "cls": "Text", "Context": "CONTAINS LEAD", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 13}) true))
(constraint (= (Respect {"id": 71, "cls": "Text", "Context": "NO TRESPASSING", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 14}) true))
(constraint (= (Respect {"id": 74, "cls": "Text", "Context": "by HOTRODZ", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 10}) true))
(constraint (= (Respect {"id": 76, "cls": "Text", "Context": "CUSTOMER", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 8}) true))
(constraint (= (Respect {"id": 77, "cls": "Text", "Context": "OR VEHICLES", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 11}) true))
(constraint (= (Respect {"id": 79, "cls": "Text", "Context": "HOTRODZ", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 7}) true))
(constraint (= (Respect {"id": 88, "cls": "Text", "Context": "NO BAR OR RESTAURANT PARKING", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 28}) true))

(constraint (= (Respect {"id": 70, "cls": "Text", "Context": "PRIVATE PROPERTY", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 16}) false))
(constraint (= (Respect {"id": 72, "cls": "Text", "Context": "10 MINUTE", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 9}) false))
(constraint (= (Respect {"id": 73, "cls": "Text", "Context": "720.404.3843", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 12}) false))
(constraint (= (Respect {"id": 83, "cls": "Text", "Context": "$100.00 FEE PER CITY ORDINANCE", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 30}) false))
(constraint (= (Respect {"id": 85, "cls": "Text", "Context": "THIS IS YOUR WARNING! 24/7", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 26}) false))

(check-synth)
