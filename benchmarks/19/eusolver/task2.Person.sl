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
		(StartAge Int (12 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 44 46 47 49 51 53 59 62 67 68 69))
    )
)

; I/O
; +
(declare-var x13 OBJ)
(declare-var x14 OBJ)
(declare-var x17 OBJ)
(declare-var x18 OBJ)
(declare-var x19 OBJ)
(declare-var x20 OBJ)
; -
(declare-var x3 OBJ)
(declare-var x21 OBJ)
(declare-var x30 OBJ)
(declare-var x32 OBJ)
(declare-var x35 OBJ)
(declare-var x57 OBJ)
(declare-var x63 OBJ)
(declare-var x65 OBJ)
(declare-var x69 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 13, "cls": "Person", "Male": True, "Age": 42, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 14, "cls": "Person", "Male": False, "Age": 28, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 17, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 18, "cls": "Person", "Male": True, "Age": 62, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 19, "cls": "Person", "Male": True, "Age": 18, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 20, "cls": "Person", "Male": True, "Age": 46, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))

(constraint (= (Respect {"id": 3, "cls": "Person", "Male": True, "Age": 24, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 21, "cls": "Person", "Male": True, "Age": 39, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 30, "cls": "Person", "Male": True, "Age": 53, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 32, "cls": "Person", "Male": True, "Age": 47, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperPlaid", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 35, "cls": "Person", "Male": True, "Age": 46, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 57, "cls": "Person", "Male": True, "Age": 67, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 63, "cls": "Person", "Male": False, "Age": 26, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 65, "cls": "Person", "Male": True, "Age": 44, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 69, "cls": "Person", "Male": False, "Age": 30, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": True}) false))

(check-synth)
