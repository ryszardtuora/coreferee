import argparse
from typing import List
from pathlib import Path
from spacy.tokens import Doc

import coreferee
import spacy

nlp = spacy.load('pl_core_news_lg')
nlp.add_pipe('coreferee')


class MentionEvaluator:
    def __init__(self):
        self.tp, self.fp, self.fn = 0, 0, 0

    def update(self, predicted_mentions, gold_mentions):
        print({
            'p': predicted_mentions,
            'g': gold_mentions,
            'intersect': predicted_mentions & gold_mentions,
            'predicted - gold': predicted_mentions - gold_mentions
        })
        predicted_mentions = set(predicted_mentions)
        gold_mentions = set(gold_mentions)
        self.tp += len(predicted_mentions & gold_mentions)
        self.fp += len(predicted_mentions - gold_mentions)
        self.fn += len(gold_mentions - predicted_mentions)

    def get_f1(self):
        pr = self.get_precision()
        rec = self.get_recall()
        return 2 * pr * rec / (pr + rec) if pr + rec > 0 else 0.0

    def get_recall(self):
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

    def get_precision(self):
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

    def get_prf(self):
        return self.get_precision(), self.get_recall(), self.get_f1()


def ann_line2mention(line):
    mention_id, mention_span, mention_text = line.split('\t')
    mention_span = [index for index in mention_span.split(' ')[1:]]  # int(index)
    return mention_id, mention_span, mention_text


def mentions_from_doc(doc: Doc) -> List[str]:
    mentions = []
    for chain in doc._.coref_chains:
        for mention in chain:
            mentions.append(
                ' '.join(
                    [str(doc[ind]) for ind in mention.token_indexes]
                )
            )
    return mentions


def eval_coreferee(test_dir: Path):
    me = MentionEvaluator()
    for p in test_dir.iterdir():
        print(p)
        if p.suffix == '.txt':
            with open(p, encoding='utf-8') as f:
                text = f.read()

            doc = nlp(text)
            predicted_mentions = mentions_from_doc(doc)
            gold_mentions = load_gold_from_ann(p.with_suffix('.ann'))
            gold_mentions_str = [mention[1] for mention in gold_mentions.values()]
            me.update(predicted_mentions, gold_mentions_str)
    return {
        'mention_f1': me.get_f1(),
        'mention_pr': me.get_precision(),
        'mention_re': me.get_recall()
    }


def load_gold_from_ann(ann_file: Path):
    with open(ann_file, encoding='utf-8') as f:
        text = f.read()
    mentions = [_ for _ in filter(lambda s: s and s[0] in ['T'], text.split('\n'))]
    clusters = [_ for _ in filter(lambda s: s and s[0] in ['*'], text.split('\n'))]
    mentions = {
        mention_id: (mention_span, mention_text) for
        mention_id, mention_span, mention_text in
        [ann_line2mention(mention) for mention in mentions]
    }
    return mentions


parser = argparse.ArgumentParser()
parser.add_argument(
    "test_dir_path",
    help="""
    """
)
args = parser.parse_args()
print(
    eval_coreferee(
        Path(args.test_dir_path)
    )
)
