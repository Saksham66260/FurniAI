"""
Seed expanded RAG knowledge chunks for FurniAI catalog products.
Document types: assembly_manual, care_guide, FAQ, related_product_knowledge
"""

from app.db.database import SessionLocal
from app.models.knowledge import KnowledgeChunk
from app.services.embedding_service import embed_text

EXPANDED_KNOWLEDGE = [
    # Product 2: Walnut Study Desk
    {
        "product_id": 2,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Instructions for Walnut Study Desk: Step 1: Unpack all solid walnut leg frames "
            "and tabletop on a soft, padded surface to prevent scratching. Step 2: Align the pre-drilled "
            "steel brackets to the underside of the desktop and insert the included M6 hex bolts. "
            "Step 3: Tighten with the provided Allen wrench until snug, do not overtighten. "
            "Step 4: Attach the cable management tray under the rear grommet. Total assembly time: ~20 minutes."
        ),
    },
    {
        "product_id": 2,
        "document_type": "care_guide",
        "content": (
            "Care & Maintenance for Walnut Study Desk: Solid walnut features a natural matte oil finish. "
            "Wipe clean weekly with a dry microfiber cloth. For water spills, blot immediately with a soft, "
            "damp cloth. Reapply natural beeswax or organic mineral oil every 6 months to preserve rich grain "
            "and protect against humidity changes. Never use alcohol or ammonia-based cleaners."
        ),
    },
    {
        "product_id": 2,
        "document_type": "FAQ",
        "content": (
            "Walnut Study Desk FAQ: Q: Can this desk accommodate dual monitors? "
            "A: Yes, the heavy-duty walnut desktop supports up to 85 kg (187 lbs) and accommodates dual "
            "27-inch monitor clamps. Q: Is assembly required? A: Minimal leg attachment is required; "
            "all necessary hardware and hex keys are included in the packaging."
        ),
    },

    # Product 3: Ergonomic Office Chair
    {
        "product_id": 3,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Instructions for Ergonomic Office Chair: 1. Push the 5 nylon caster wheels firmly "
            "into the reinforced five-star star base. 2. Insert the Class-4 gas lift cylinder vertically "
            "into the base hub. 3. Fasten the 3D lumbar support backrest to the high-density foam seat pan "
            "using 4 hex bolts. 4. Place assembled seat unit onto the gas cylinder. Test height adjustment lever."
        ),
    },
    {
        "product_id": 3,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Ergonomic Office Chair: Vacuum breathable Korean mesh backrest monthly using "
            "a brush attachment. Spot clean stains with mild fabric foam shampoo and lukewarm water. "
            "Check and retighten armrest bolts every 6 months for optimal ergonomic stability."
        ),
    },
    {
        "product_id": 3,
        "document_type": "FAQ",
        "content": (
            "Ergonomic Chair FAQ: Q: What is the maximum user weight limit? A: The chair is BIFMA certified "
            "for continuous daily use up to 135 kg (300 lbs). Q: Does it have dynamic lumbar adjustment? "
            "A: Yes, the self-adjusting adaptive lumbar system flexes to support lower spine posture throughout the day."
        ),
    },

    # Product 5: Round Oak Dining Table
    {
        "product_id": 5,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Manual for Round Oak Dining Table: Invert the round white oak top onto a protective rug. "
            "Fasten the four interlocking architectural pedestal legs to the central steel mounting disc using "
            "M8 bolts and locking washers. Secure the pedestal assembly to the tabletop. Two adults recommended "
            "to carefully flip the table right side up."
        ),
    },
    {
        "product_id": 5,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Round Oak Dining Table: Protect the white oak surface from hot pans and mugs using "
            "trivets or coasters. Clean with mild soapy water and dry immediately with a clean lint-free towel. "
            "Avoid direct sunlight exposure to prevent uneven wood patina."
        ),
    },
    {
        "product_id": 5,
        "document_type": "FAQ",
        "content": (
            "Round Oak Dining Table FAQ: Q: How many chairs comfortably fit around this table? "
            "A: The 120cm diameter comfortably seats 4 to 5 adults. Q: Is the wood sustainably harvested? "
            "A: Yes, crafted from 100% FSC-certified European white oak with non-toxic zero-VOC lacquer."
        ),
    },

    # Product 6: Contemporary Black Velvet 2-Seater
    {
        "product_id": 6,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Velvet 2-Seater Sofa: Brush velvet fabric gently in the direction of the nap "
            "using a soft bristled clothes brush. For liquid spills, press an absorbent clean paper towel "
            "without rubbing. For crushed velvet pile, steam lightly from a 15 cm distance."
        ),
    },
    {
        "product_id": 6,
        "document_type": "FAQ",
        "content": (
            "Contemporary Velvet Sofa FAQ: Q: Are the seat cushion covers removable and washable? "
            "A: Cushion covers have concealed zippers for dry cleaning only. Machine washing is not recommended. "
            "Q: What is the Martindale rub count? A: Heavy commercial grade rating of 45,000 rubs."
        ),
    },

    # Product 10: Minimalist White Walnut Computer Desk
    {
        "product_id": 10,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Manual for Minimalist White Walnut Computer Desk: Requires screwdriver and included Allen key. "
            "Attach the matte white powder-coated steel legs to the walnut desktop frame. Mount the soft-closing "
            "storage drawer slides according to index markers A and B. Level the adjustable feet on uneven floors."
        ),
    },
    {
        "product_id": 10,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Minimalist Computer Desk: Dual-tone surface with UV-resistant matte lacquer. "
            "Clean with microfiber cloth dampened with warm water. Avoid chemical solvents, acetone, or abrasive sponges."
        ),
    },

    # Product 12: Scandinavian Brown Leather Office Chair
    {
        "product_id": 12,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Guide for Scandinavian Leather Office Chair: Insert casters into aluminum base. Insert hydraulic "
            "piston. Attach curved top-grain leather shell to synchronous tilt mechanism with 4 heavy-duty bolts. "
            "Place shell on piston until firmly seated."
        ),
    },
    {
        "product_id": 12,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Brown Leather Chair: Genuine top-grain aniline leather. Condition twice yearly with "
            "a specialized leather balm to preserve softness and patina. Keep away from direct heat sources and radiators."
        ),
    },
    {
        "product_id": 12,
        "document_type": "FAQ",
        "content": (
            "Leather Office Chair FAQ: Q: Is the leather genuine or bonded? A: 100% genuine top-grain cowhide leather. "
            "Q: Does the tilt lock in multiple positions? A: Yes, 3-position synchronous tilt with tension control knob."
        ),
    },

    # Product 13: Industrial Natural Oak Writing Desk
    {
        "product_id": 13,
        "document_type": "assembly_manual",
        "content": (
            "Assembly Guide for Industrial Natural Oak Writing Desk: Connect steel trapezoid leg frames with the rear "
            "cross-brace. Secure the solid oak tabletop with M6 bolts. Insert magnetic cable management clips."
        ),
    },
    {
        "product_id": 13,
        "document_type": "care_guide",
        "content": (
            "Care Guide for Industrial Oak Writing Desk: Dust regularly. Avoid placing pens directly without a desk pad "
            "to prevent indentation. Clean with damp cloth and dry immediately."
        ),
    },
    {
        "product_id": 13,
        "document_type": "FAQ",
        "content": (
            "Natural Oak Writing Desk FAQ: Q: What is the clearance height under the desk? A: 72 cm (28.3 inches) "
            "comfortable for standard office chairs with armrests. Q: Does it fit in small rooms? A: Compact 110 x 60 cm "
            "footprint designed specifically for space-conscious apartments."
        ),
    },
]


def expand_knowledge():
    db = SessionLocal()
    try:
        inserted = 0
        for item in EXPANDED_KNOWLEDGE:
            # Check if identical chunk exists to avoid duplicates
            existing = (
                db.query(KnowledgeChunk)
                .filter(
                    KnowledgeChunk.product_id == item["product_id"],
                    KnowledgeChunk.document_type == item["document_type"],
                )
                .first()
            )

            if existing:
                # Update content & embedding
                existing.content = item["content"]
                existing.embedding = embed_text(item["content"])
            else:
                embedding = embed_text(item["content"])
                chunk = KnowledgeChunk(
                    product_id=item["product_id"],
                    document_type=item["document_type"],
                    content=item["content"],
                    embedding=embedding,
                )
                db.add(chunk)
                inserted += 1

        db.commit()
        total_chunks = db.query(KnowledgeChunk).count()
        print(f"Successfully processed knowledge chunks. Total chunks in DB: {total_chunks}")

    except Exception as e:
        db.rollback()
        print(f"Error expanding knowledge: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    expand_knowledge()
