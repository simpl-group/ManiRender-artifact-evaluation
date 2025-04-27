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
			; Person
			(Male x)
			(AgeLess x StartAge)
			(AgeGreater x StartAge)
			(AgeEq x StartAge)
			(Orientation x StartOrientation)
			(Glasses x)
			(Hat x)
			(HoldObjectsInFront x)
			(Bag x StartBag)
			(TopStyle x StartTopStyle)
			(BottomStyle x StartBottomStyle)
			(ShortSleeve x)
			(LongSleeve x)
			(LongCoat x)
			(Trousers x)
			(Shorts x)
			(SkirtDress x)
			(Boots x)
        ))

        ; terminals
		;Person
		(StartOrientation String ("Front" "Back" "Side"))
		(StartBag String ("BackPack" "ShoulderBag" "HandBag" "NoBag"))
		(StartTopStyle String ("UpperStride" "UpperLogo" "UpperPlaid" "UpperSplice" "NoTopStyle"))
		(StartBottomStyle String ("BottomStripe" "BottomPattern" "NoBottomStyle"))
		(StartAge Int (0 18 20 21 25 26 27 28 29 30 31 33 34 35 36 37 39 40 41 42 43 46 48 63 64 65))
    )
)

; I/O
; +
(declare-var x19 OBJ)
(declare-var x28 OBJ)
(declare-var x40 OBJ)
; -
(declare-var x21 OBJ)
(declare-var x27 OBJ)
(declare-var x29 OBJ)
(declare-var x32 OBJ)
(declare-var x41 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 19, "cls": "Person", "Male": True, "Age": 43, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 28, "cls": "Person", "Male": True, "Age": 64, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 40, "cls": "Person", "Male": True, "Age": 40, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))

(constraint (= (Respect {"id": 21, "cls": "Person", "Male": False, "Age": 46, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 27, "cls": "Person", "Male": True, "Age": 48, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 29, "cls": "Person", "Male": True, "Age": 42, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 32, "cls": "Person", "Male": False, "Age": 41, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 41, "cls": "Person", "Male": True, "Age": 39, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))

(check-synth)
