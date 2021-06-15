
from typing import List, Dict, Sequence

class Matrics:
    def __init__(self, sents_true_labels: Sequence[Sequence[Dict]], sents_pred_labels:Sequence[Sequence[Dict]]):
        self.sents_true_labels = sents_true_labels
        self.sents_pred_labels = sents_pred_labels 
        self.types = set(entity['label'] for sent in sents_true_labels for entity in sent)
        self.confusion_matrices = {type: {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0} for type in self.types}
        self.scores = {type: {'p': 0, 'r': 0, 'f1': 0} for type in self.types}

    def cal_confusion_matrices(self) -> Dict[str, Dict]:
        """Calculate confusion matrices for all sentences."""
        for true_labels, pred_labels in zip(self.sents_true_labels, self.sents_pred_labels):
            for true_label in true_labels: 
                entity_type = true_label['label']
                prediction_hit_count = 0 
                for pred_label in pred_labels:
                    if pred_label['label'] != entity_type:
                        continue
                    if pred_label['start_idx'] == true_label['start_idx'] and pred_label['end_idx'] == true_label['end_idx'] and pred_label['text'] == true_label['text']: # TP
                        self.confusion_matrices[entity_type]['TP'] += 1
                        prediction_hit_count += 1
                    elif ((pred_label['start_idx'] == true_label['start_idx']) or (pred_label['end_idx'] == true_label['end_idx'])) and pred_label['text'] != true_label['text']: # boundry error, count FN, FP
                        self.confusion_matrices[entity_type]['FP'] += 1
                        self.confusion_matrices[entity_type]['FN'] += 1
                        prediction_hit_count += 1
                if prediction_hit_count != 1: # FN, model cannot make a prediction for true_label
                    self.confusion_matrices[entity_type]['FN'] += 1
                prediction_hit_count = 0 # reset to default

    def cal_scores(self) -> Dict[str, Dict]:
        """Calculate precision, recall, f1."""
        confusion_matrices = self.confusion_matrices 
        scores = {type: {'p': 0, 'r': 0, 'f1': 0} for type in self.types}
        
        for entity_type, confusion_matrix in confusion_matrices.items():
            if confusion_matrix['TP'] == 0 and confusion_matrix['FP'] == 0:
                scores[entity_type]['p'] = 0
            else:
                scores[entity_type]['p'] = confusion_matrix['TP'] / (confusion_matrix['TP'] + confusion_matrix['FP'])

            if confusion_matrix['TP'] == 0 and confusion_matrix['FN'] == 0:
                scores[entity_type]['r'] = 0
            else:
                scores[entity_type]['r'] = confusion_matrix['TP'] / (confusion_matrix['TP'] + confusion_matrix['FN']) 

            if scores[entity_type]['p'] == 0 or scores[entity_type]['r'] == 0:
                scores[entity_type]['f1'] = 0
            else:
                scores[entity_type]['f1'] = 2*scores[entity_type]['p']*scores[entity_type]['r'] / (scores[entity_type]['p']+scores[entity_type]['r'])  
        self.scores = scores

    def print_confusion_matrices(self):
        for entity_type, matrix in self.confusion_matrices.items():
            print(f"{entity_type}: {matrix}")

    def print_scores(self):
        for entity_type, score in self.scores.items():
            print(f"{entity_type}: f1 {score['f1']:.4f}, precision {score['p']:.4f}, recall {score['r']:.4f}")
