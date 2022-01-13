# Copyright 2021 msg systems ag

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from coreferencer.data_model import Mention
from coreferencer.rules import RulesAnalyzerFactory
from coreferencer.test_utils import get_nlps

class CommonDataModelTest(unittest.TestCase):

    def setUp(self):

        for nlp in (nlp for nlp in get_nlps('en') if nlp.meta['name'] == 'core_web_sm'):
            self.sm_nlp = nlp
            self.sm_rules_analyzer = RulesAnalyzerFactory().get_rules_analyzer(nlp)

    def test_representations_doc(self):
        doc = self.sm_nlp('Richard and Peter said they had finished')
        self.assertEqual('[0: [0, 2], [4]]', str(doc._.coref_chains))
        self.assertEqual('[0: [0, 2], [4]]', str(doc[0]._.coref_chains))
        self.assertEqual('0: [0, 2], [4]', str(doc._.coref_chains[0]))
        self.assertEqual('0: [0, 2], [4]', str(doc[0]._.coref_chains[0]))
        self.assertEqual('[0, 2]', str(doc._.coref_chains[0].mentions[0]))
        self.assertEqual('[0, 2]', str(doc[0]._.coref_chains[0].mentions[0]))
        self.assertEqual('[4]', str(doc._.coref_chains[0].mentions[1]))
        self.assertEqual('[4]', str(doc[0]._.coref_chains[0].mentions[1]))
        self.assertEqual('[Richard(0); Peter(2)]',
            doc._.coref_chains[0].mentions[0].pretty_representation)
        self.assertEqual('[Richard(0); Peter(2)]',
            doc[0]._.coref_chains[0].mentions[0].pretty_representation)
        self.assertEqual('0: [Richard(0); Peter(2)], they(4)',
            doc._.coref_chains[0].pretty_representation)
        self.assertEqual('0: [Richard(0); Peter(2)], they(4)',
            doc[0]._.coref_chains[0].pretty_representation)
        self.assertEqual(0,
            doc[0]._.coref_chains[0].most_specific_mention_index)
        self.assertEqual([doc[0], doc[2]], doc._.coref_chains.resolve(doc[4]))

    def test_representations_token(self):
        doc = self.sm_nlp('I saw Peter. Richard and he came in. They had arrived')
        self.assertEqual(2, len(doc._.coref_chains))
        self.assertEqual('[0: [2], [6], 1: [4, 6], [10]]', str(doc._.coref_chains))
        self.assertEqual('0: Peter(2), he(6); 1: [Richard(4); he(6)], They(10)',
            doc._.coref_chains.pretty_representation)

        self.assertEqual('[0: [2], [6], 1: [4, 6], [10]]', str(doc[6]._.coref_chains))
        self.assertEqual('0: Peter(2), he(6); 1: [Richard(4); he(6)], They(10)',
            doc[6]._.coref_chains.pretty_representation)

        self.assertEqual('[0: [2], [6]]', str(doc[2]._.coref_chains))
        self.assertEqual('0: Peter(2), he(6)',
            doc[2]._.coref_chains.pretty_representation)

        self.assertEqual('[1: [4, 6], [10]]', str(doc[10]._.coref_chains))
        self.assertEqual('1: [Richard(4); he(6)], They(10)',
            doc[10]._.coref_chains.pretty_representation)

        self.assertEqual(0,
            doc._.coref_chains[0].most_specific_mention_index)
        self.assertEqual(0,
            doc._.coref_chains[1].most_specific_mention_index)
        self.assertEqual([doc[2], doc[4]], doc._.coref_chains.resolve(doc[10]))
        self.assertEqual(None, doc._.coref_chains.resolve(doc[4]))
        self.assertEqual([doc[2]], doc._.coref_chains.resolve(doc[6]))

    def test_object_access(self):
        doc = self.sm_nlp('I saw Peter. Richard and he came in. They had arrived')
        self.assertEqual('1: [4, 6], [10]', str(doc._.coref_chains[1]))
        self.assertEqual(2, len(doc._.coref_chains))
        self.assertEqual(2, len(doc._.coref_chains[1]))
        self.assertEqual('[4, 6]', str(doc._.coref_chains[1][0]))
        self.assertEqual(2, len(doc._.coref_chains[1][0]))
        self.assertEqual(4, doc._.coref_chains[1][0][0])
        found = False
        for chain in doc._.coref_chains:
            for mention in chain.mentions:
                if mention == Mention(doc[10], False):
                    found = True
        self.assertTrue(found)

    def test_representations_cataphora(self):
        doc = self.sm_nlp('Although he had gone out, Richard came back')
        self.assertEqual('[0: [1], [6]]', str(doc._.coref_chains))
        self.assertEqual(1,
            doc._.coref_chains[0].most_specific_mention_index)
        self.assertEqual([doc[6]], doc._.coref_chains.resolve(doc[1]))
        self.assertEqual(None, doc._.coref_chains.resolve(doc[6]))

    def test_most_specific_only_nouns(self):
        doc = self.sm_nlp('I saw a big dog. The dog came in.')
        self.assertEqual('[0: [4], [7]]', str(doc._.coref_chains))
        self.assertEqual(0,
            doc._.coref_chains[0].most_specific_mention_index)
        self.assertEqual([doc[4]], doc._.coref_chains.resolve(doc[7]))
        self.assertEqual(None, doc._.coref_chains.resolve(doc[4]))

    def test_most_specific_only_entity(self):
        doc = self.sm_nlp('I spoke to Mr. Platt. The man came in.')
        self.assertEqual('[0: [4], [7]]', str(doc._.coref_chains))
        self.assertEqual(0,
            doc._.coref_chains[0].most_specific_mention_index)
        self.assertEqual([doc[4]], doc._.coref_chains.resolve(doc[7]))
        self.assertEqual(None, doc._.coref_chains.resolve(doc[4]))

    def test_resolve_recursive(self):
        doc = self.sm_nlp('I spoke to Mr. Platt. The man and Richard came in. They and Peter said hello. They were all here.')
        self.assertEqual([doc[4], doc[9], doc[15]], doc._.coref_chains.resolve(doc[19]))

    def test_representations_cataphora(self):
        doc = self.sm_nlp('Although he had gone out, Richard came back')
        self.assertEqual('[0: [1], [6]]', str(doc._.coref_chains))
        self.assertEqual(1,
            doc._.coref_chains[0].most_specific_mention_index)
        self.assertEqual([doc[6]], doc._.coref_chains.resolve(doc[1]))
        self.assertEqual(None, doc._.coref_chains.resolve(doc[6]))
