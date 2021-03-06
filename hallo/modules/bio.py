from hallo.events import EventMessage
from hallo.function import Function


class Protein(Function):
    """
    Takes, as input, a list of nucleotide bases, and outputs amino acid strings
    """

    START = "START"
    STOP = "STOP"

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "protein"
        # Names which can be used to address the Function
        self.names = {"protein", "prot", "amino acid"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Convert a set of nucleobases to a string of amino acids"

    def run(self, event):
        codon_table = {
            "Ala": ["GCU", "GCC", "GCA", "GCG"],
            "Arg": ["CGU", "CGC", "CGA", "CGG", "AGA", "AGG"],
            "Asn": ["AAU", "AAC"],
            "Cys": ["UGU", "UGC"],
            "Gln": ["CAA", "CAG"],
            "Glu": ["GAA", "GAG"],
            "Gly": ["GGU", "GGC", "GGA", "GGG"],
            "His": ["CAU", "CAC"],
            "Ile": ["AUU", "AUC", "AUA"],
            Protein.START: ["AUG"],
            "Leu": ["UUA", "UUG", "CUU", "CUC", "CUA", "CUG"],
            "Lys": ["AAA", "AAG"],
            "Met": ["AUG"],
            "Phe": ["UUU", "UUC"],
            "Pro": ["CCU", "CCC", "CCA", "CCG"],
            "Ser": ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"],
            "Thr": ["ACU", "ACC", "ACA", "ACG"],
            "Trp": ["UGG"],
            "Tyr": ["UAU", "UAC"],
            "Val": ["GUU", "GUC", "GUA", "GUG"],
            Protein.STOP: ["UAA", "UGA", "UAG"],
        }
        # Clean the string, replace Thymine with Uracil
        line_clean = event.command_args.upper().replace("T", "U")
        if not all([c in "ACGU" for c in line_clean]):
            return event.create_response("Error, invalid nucleotides.")
        strand = ["..."]
        if codon_table[Protein.START][0] in line_clean:
            strand = [Protein.START]
            line_clean = line_clean.split(codon_table[Protein.START][0])[-1]
        stop = False
        while len(line_clean) >= 3 and not stop:
            codon = line_clean[:3]
            line_clean = line_clean[3:]
            for protein in codon_table:
                if codon in codon_table[protein]:
                    strand += [protein]
                    if protein == Protein.STOP:
                        stop = True
                    break
        if not stop:
            strand += ["..."]
        return event.create_response("-".join(strand))

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return None
        clean_line = event.text.strip().upper()
        if len(clean_line) < 3:
            return None
        valid_chars = list("ACGUT")
        check_message = clean_line
        for valid_char in valid_chars:
            check_message = check_message.replace(valid_char, "")
        if check_message == "":
            event.split_command_text("", clean_line)
            return self.run(event)
        return None
