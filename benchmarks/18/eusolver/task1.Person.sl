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
		(StartAge Int (21 22 23 24 25 31 34 35 36 37 39 40 42 45 50 53 54 55 62 65))
    )
)

; I/O
; +
(declare-var x2 OBJ)
(declare-var x5 OBJ)
(declare-var x7 OBJ)
(declare-var x17 OBJ)
(declare-var x24 OBJ)
; -
(declare-var x1 OBJ)
(declare-var x12 OBJ)
(declare-var x16 OBJ)
(declare-var x20 OBJ)
(declare-var x25 OBJ)
(declare-var x34 OBJ)
(declare-var x35 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 2, "cls": "Person", "Male": False, "Age": 23, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) true))
(constraint (= (Respect {"id": 5, "cls": "Person", "Male": False, "Age": 22, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 7, "cls": "Person", "Male": True, "Age": 23, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 17, "cls": "Person", "Male": False, "Age": 22, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 24, "cls": "Person", "Male": False, "Age": 22, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))

(constraint (= (Respect {"id": 1, "cls": "Person", "Male": False, "Age": 54, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 12, "cls": "Person", "Male": False, "Age": 21, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "HandBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 16, "cls": "Person", "Male": False, "Age": 40, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "UpperSplice", "BottomStyle": "BottomPattern", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 20, "cls": "Person", "Male": True, "Age": 22, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": True, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 25, "cls": "Person", "Male": False, "Age": 36, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 34, "cls": "Person", "Male": False, "Age": 31, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 35, "cls": "Person", "Male": True, "Age": 23, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": True}) false))

(check-synth)
