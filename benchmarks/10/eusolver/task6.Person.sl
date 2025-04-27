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
		(StartAge Int (0 17 18 19 20 21 22 23 24 25 26 27 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 45 46 47 49 50 52 54 56 58 60 63 64 68 69 71 74))
    )
)

; I/O
; +
(declare-var x2 OBJ)
(declare-var x19 OBJ)
(declare-var x24 OBJ)
(declare-var x36 OBJ)
(declare-var x37 OBJ)
; -
(declare-var x7 OBJ)
(declare-var x14 OBJ)
(declare-var x20 OBJ)
(declare-var x23 OBJ)
(declare-var x28 OBJ)
(declare-var x29 OBJ)
(declare-var x64 OBJ)
(declare-var x65 OBJ)
(declare-var x76 OBJ)
(declare-var x84 OBJ)
(declare-var x87 OBJ)
(declare-var x94 OBJ)
(declare-var x96 OBJ)
(declare-var x100 OBJ)
(declare-var x101 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 2, "cls": "Person", "Male": True, "Age": 42, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 19, "cls": "Person", "Male": True, "Age": 24, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 24, "cls": "Person", "Male": False, "Age": 43, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 36, "cls": "Person", "Male": True, "Age": 29, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 37, "cls": "Person", "Male": True, "Age": 30, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))

(constraint (= (Respect {"id": 7, "cls": "Person", "Male": True, "Age": 34, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperStride", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 14, "cls": "Person", "Male": False, "Age": 42, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 20, "cls": "Person", "Male": True, "Age": 34, "Orientation": "Front", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 23, "cls": "Person", "Male": True, "Age": 37, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 28, "cls": "Person", "Male": False, "Age": 45, "Orientation": "Front", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": 5, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 29, "cls": "Person", "Male": True, "Age": 50, "Orientation": "Front", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 64, "cls": "Person", "Male": False, "Age": 46, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 65, "cls": "Person", "Male": True, "Age": 23, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 76, "cls": "Person", "Male": False, "Age": 24, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 84, "cls": "Person", "Male": True, "Age": 19, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 87, "cls": "Person", "Male": True, "Age": 25, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 94, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 96, "cls": "Person", "Male": True, "Age": 33, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 100, "cls": "Person", "Male": True, "Age": 26, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 101, "cls": "Person", "Male": True, "Age": 20, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))

(check-synth)
