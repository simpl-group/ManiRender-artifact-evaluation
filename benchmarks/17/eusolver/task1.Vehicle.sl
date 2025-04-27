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
(declare-var x2 OBJ)
(declare-var x15 OBJ)
(declare-var x55 OBJ)
; -
(declare-var x1 OBJ)
(declare-var x7 OBJ)
(declare-var x8 OBJ)
(declare-var x10 OBJ)
(declare-var x11 OBJ)
(declare-var x18 OBJ)
(declare-var x19 OBJ)
(declare-var x23 OBJ)
(declare-var x24 OBJ)
(declare-var x25 OBJ)
(declare-var x26 OBJ)
(declare-var x27 OBJ)
(declare-var x29 OBJ)
(declare-var x36 OBJ)
(declare-var x38 OBJ)
(declare-var x43 OBJ)
(declare-var x48 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 2, "cls": "Vehicle", "Color": "Black", "Type": "Pickup"}) true))
(constraint (= (Respect {"id": 15, "cls": "Vehicle", "Color": "Blue", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 55, "cls": "Vehicle", "Color": "Blue", "Type": "MPV"}) true))

(constraint (= (Respect {"id": 1, "cls": "Vehicle", "Color": "Black", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 7, "cls": "Vehicle", "Color": "Black", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 8, "cls": "Vehicle", "Color": "Red", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 10, "cls": "Vehicle", "Color": "White", "Type": "Pickup"}) false))
(constraint (= (Respect {"id": 11, "cls": "Vehicle", "Color": "White", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 18, "cls": "Vehicle", "Color": "White", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 19, "cls": "Vehicle", "Color": "Black", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 23, "cls": "Vehicle", "Color": "Gray", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 24, "cls": "Vehicle", "Color": "Golden", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 25, "cls": "Vehicle", "Color": "Gray", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 26, "cls": "Vehicle", "Color": "Red", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 27, "cls": "Vehicle", "Color": "Blue", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 29, "cls": "Vehicle", "Color": "Red", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 36, "cls": "Vehicle", "Color": "Golden", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 38, "cls": "Vehicle", "Color": "Golden", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 43, "cls": "Vehicle", "Color": "Green", "Type": "Pickup"}) false))
(constraint (= (Respect {"id": 48, "cls": "Vehicle", "Color": "White", "Type": "Sedan"}) false))

(check-synth)
