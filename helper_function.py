import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from prompt_template import prompt_template

load_dotenv()


class State(TypedDict):
    text: str
    chunks: List[str]

class Chunks(BaseModel):
    chunks: List[str]

llm = ChatOllama(model=os.getenv('MODEL'), temperature=0)

prompt = ChatPromptTemplate.from_template(
    '''
    Your job is to split the provided text into a list of smaller consecutive chunks.
    
    CRITICAL RULES:
    1. Do not skip, summarize, or alter any words. Every single sentence from the original text must appear in order across the chunks.
    2. Each chunk must be less than 2000 characters.
    3. Do not include chunk numbers (e.g., "Chunk 1") or introductory text.
    4. Do not add "..." at the start or end of the chunks.
    5. Return the result strictly as the requested structured list of chunks.

    text: {text}
    '''
)


def chunking(State):
    message = prompt.invoke(State["text"])

    structured_llm = llm.with_structured_output(Chunks)

    response = structured_llm.invoke(message)

    return {"chunks": response.chunks}


builder = StateGraph(State)
builder.add_node("chunker", chunking)

builder.add_edge(START, "chunker")
builder.add_edge("chunker", END)

graph = builder.compile()

def helper_chunk(text):
    response = graph.invoke({"text": text})

    output_text = response["chunks"]

    return output_text

if __name__ == "__main__":
    print(helper_chunk(
        """
            The solar winds of the Aethel-Stream did not blow; they sang.

            Captain Lyra Vance stood on the open-air quarterdeck of *The Star-Catcher*, her long coat snapping against the cosmic gale. She held no steering wheel, but rather a crystalline harp bolted to the deck. Her fingers danced across the glowing, light-woven strings, sending micro-pulses of harmonic resonance down into the ship’s solar sails. The massive, iridescent sheets of celestial silk shifted, catching a sudden gust of stardust that propelled the wooden galleon smoothly over the crest of a dark matter wave.

            Around them, the Void was not black, but a deep, bruised violet, illuminated by the bioluminescent nebulae that drifted like giant, glowing jellyfish through the ether.

            "Hold fast, crew!" Lyra called out, her voice amplified by an enchantment forged into her silver throat-comm. "The reef is ahead!"

            Below her on the main deck, Kaelen, a stony-skinned dwarf from the asteroid-forges of Nidavellir, locked the ether-cannons into place. These weapons fired no cannonballs, but condensed spheres of pure gravity, designed to shatter the rogue comets threatening their path.

            They were hunting the *Astraea’s Tear*, a legendary wandering comet said to be the frozen tear of a dying star-goddess. It only entered this sector once every three centuries, and it carried a core of pure, unrefined Aether-gold—enough to power an entire star-system’s protective wards for a generation.

            "Captain!" Kaelen shouted, wiping cosmic soot from his brow. "The Void-Whales are migrating early! We're coming right up on a pod!"

            Out of the swirling violet fog, massive shapes materialized. They were easily the size of dreadnoughts, their skin shimmering with ancient constellations. The stellar leviathans glided through the vacuum, singing a low, bass frequency that vibrated right through the ship's timbers.

            Lyra tightened her grip on the harp. A single wrong note would alter their trajectory, sending them colliding into a multi-ton beast, or worse, triggering the aggressive defense mechanism of the pod's alpha.

            Closing her eyes, she listened to the rhythm of the universe. She didn't fight the current; she joined it. She struck a chord of perfect compliance—a soft, lyrical melody that mirrored the whales' own ancient song. *The Star-Catcher* dipped its bow, gracefully weaving under the belly of a massive calf whose tail brushed the ship’s mast, leaving a trail of sparkling, harmless stardust in its wake.

            "Clear!" Kaelen cheered.

            But their victory was short-lived. The temperature on deck plummeted. The violet sky turned a sickening, abyssal black.

            "Wraiths," Lyra hissed, her knuckles turning white on the harp.

            From the shadows of a nearby dead moon, three obsidian corvettes emerged. They belonged to the Void-Scourge—pirates who had traded their humanity for dark magic and cybernetic thrusters. They didn't want to harvest the comet; they wanted to shatter it to weaponize its chaotic energy.

            Harpoons of corrupted purple lightning slammed into *The Star-Catcher's* hull, the dark energy eating away at the protective enchantments.

            "Kaelen, fire at will!" Lyra commanded, her fingers flying across the harp strings in a furious, staccato battle hymn. The ship swung hard, the solar sails snapping like whips.

            Kaelen roared, pulling the levers on the gravity cannons. *Thoom.* *Thoom.* Spheres of localized singularity erupted from the decks, tearing into the pirate ships, crushing their metal hulls into compact cubes of scrap metal.

            But the enemy leader's ship was fast, slipping past the defenses. A boarding party of shadow-clad raiders leaped onto the deck, swords of plasma-infused steel flashing.

            Lyra drew her rapier—a blade forged from a fallen meteor that hummed with kinetic energy. She stepped away from the helm, leaving the ship to glide on its momentum. She parried a pirate's strike, the clash of blades ringing out in the pressurized air bubble surrounding the deck. With a swift twist, she channeled the ship's stored solar energy through her blade, blinding her attacker with a flash of star-fire before sending him overboard into the starry abyss.

            "The comet, Captain! It's reaching the event horizon!" Kaelen yelled, fending off two raiders with his heavy wrench.

            Lyra looked up. Ahead, a massive, brilliant blue comet was hurtling toward a swirling gravitational singularity—a cosmic whirlpool. If it fell in, it was gone forever.

            Sprinting back to the crystalline harp, she ignored the battle raging around her. She bled a few drops of her own essence onto the strings, infusing the instrument with raw willpower. She struck a final, echoing crescent chord.

            The ship didn't just sail; it leapt.

            *The Star-Catcher* soared off the crest of a gravity wave, flying right over the remaining pirate ship. Lyra leaned over the railing, casting a tether woven of pure magnetic light. The lasso caught the icy tail of the *Astraea’s Tear*.

            "Brace yourselves!"

            The ship groaned as the momentum of the massive comet yanked them forward, pulling them right along the edge of the cosmic whirlpool. For a breathless second, they hovered between oblivion and salvation. Then, with a brilliant flash of golden light, the comet’s icy shell cracked open under the tension, releasing a warm, radiant wave of Aether-gold energy that completely dissolved the darkness around them. The pirate ships crumbled to dust in the holy light.

            The tether snapped back, bringing a massive chunk of glowing gold crystal right into the cargo hold.

            As the blinding light settled, the violet sky returned, peaceful once more. *The Star-Catcher* drifted safely into the calm waters of a quiet nebula. Lyra let out a breath she felt she’d been holding for lightyears, smiling as the stardust settled in her hair like a crown.
        """))