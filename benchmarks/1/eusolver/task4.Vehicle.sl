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
			; Vehicle
			(Color x StartColor)
			(Type x StartType)
        ))

        ; terminals
		;Vehicle
		(StartColor String ("Yellow" "Orange" "Green" "Gray" "Red" "Blue" "White" "Golden" "Brown" "Black"))
		(StartType String ("Sedan" "Suv" "Van" "Hatchback" "MPV" "Pickup" "Bus" "Truck" "Estate" "Motor"))
    )
)

; I/O
; +
(declare-var x7 OBJ)
(declare-var x8 OBJ)
(declare-var x10 OBJ)
(declare-var x11 OBJ)
(declare-var x12 OBJ)
(declare-var x14 OBJ)
; -
(declare-var x1 OBJ)
(declare-var x2 OBJ)
(declare-var x4 OBJ)
(declare-var x17 OBJ)
(declare-var x27 OBJ)
(declare-var x28 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 7, "cls": "Vehicle", "Color": "Blue", "Type": "Hatchback"}) true))
(constraint (= (Respect {"id": 8, "cls": "Vehicle", "Color": "Gray", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 10, "cls": "Vehicle", "Color": "Black", "Type": "Suv"}) true))
(constraint (= (Respect {"id": 11, "cls": "Vehicle", "Color": "White", "Type": "Suv"}) true))
(constraint (= (Respect {"id": 12, "cls": "Vehicle", "Color": "Red", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 14, "cls": "Vehicle", "Color": "Red", "Type": "Hatchback"}) true))

(constraint (= (Respect {"id": 1, "cls": "Vehicle", "Color": "Blue", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 2, "cls": "Vehicle", "Color": "Black", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 4, "cls": "Vehicle", "Color": "Black", "Type": "Motor"}) false))
(constraint (= (Respect {"id": 17, "cls": "Vehicle", "Color": "White", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 27, "cls": "Vehicle", "Color": "Gray", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 28, "cls": "Vehicle", "Color": "White", "Type": "Van"}) false))

(check-synth)
