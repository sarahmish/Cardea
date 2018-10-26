import featuretools as ft
import pandas as pd

from cardea.problem_definition import ProblemDefinition


class ProlongedLengthOfStay (ProblemDefinition):
    """Defines the problem of length of stay, finding whether
        a patient stayed in the hospital more or less than a week (Default).

        Attributes:
        target_label: The target label of the prediction problem.
        target_entity: Name of the entity containing the target label.
        cutoff_time_label: The cutoff time label of the prediction problem.
        cutoff_entity: Name of the entity containing the cutoff time label.
        prediction_type: The type of the machine learning prediction.
        """

    updated_es = None
    target_label = 'length'
    target_entity = 'Encounter'
    cutoff_time_label = 'start'
    cutoff_entity = 'Period'
    prediction_type = 'classification'

    def __init__(self, t=7):
        self.threshold = t

    def generate_cutoff_times(self, es):
        """Generates cutoff times for the predection problem.

            Args:
            es: fhir entityset.

            Returns:
            entity_set, target_entity, series of target_labels and a dataframe of cutoff_times.

            Raises:
            ValueError: An error occurs if the cutoff variable does not exist.
            """

        if (self.check_target_label(es,
                                    self.target_entity,
                                    self.target_label) and not
            self.check_target_label_values(es,
                                           self.target_entity,
                                           self.target_label)):
            if self.check_target_label(
                    es,
                    self.cutoff_entity,
                    self.cutoff_time_label):

                instance_id = list(es[self.target_entity].df.index)
                cutoff_times = es[self.cutoff_entity].df[self.cutoff_time_label].to_frame()
                cutoff_times['instance_id'] = instance_id
                cutoff_times.columns = ['cutoff_time', 'instance_id']
                update_es = es[self.target_entity].df

                # threshold
                update_es['length'] = (update_es['length'] >= self.threshold)
                update_es['length'] = update_es['length'].astype(int)

                es = es.entity_from_dataframe(entity_id=self.target_entity,
                                              dataframe=update_es,
                                              index='identifier')
                cutoff_times['label'] = list(es[self.target_entity].df[self.target_label])
                return(es, self.target_entity, cutoff_times)
            else:
                raise ValueError('Cutoff time label {} in table {} does not exist'
                                 .format(self.cutoff_time_label, self.target_entity))

        else:
            updated_es = self.generate_target_label(es)
            return self.generate_cutoff_times(updated_es)

    def generate_target_label(self, es):
        """Generates target labels in the case of having missing label in the entityset.

            Args:
            es: fhir entityset.
            target_label: The target label of the prediction problem.
            target_entity: Name of the entity containing the target label.

            Returns:
            Updated entityset with the generated label.

            Raises:
            ValueError: An error occurs if the target label cannot be generated.
            """
        generate_from = 'Period'
        start = 'start'
        end = 'end'

        if (self.check_target_label(
            es,
            generate_from,
            start) and self.check_target_label(es,
                                               generate_from,
                                               end)):

            if (not self.check_target_label_values(
                    es,
                    generate_from,
                    start) and not self.check_target_label_values(es,
                                                                  generate_from,
                                                                  end)):

                es[generate_from].df[start] = pd.to_datetime(
                    es[generate_from]
                    .df[start])
                es[generate_from].df[end] = pd.to_datetime(
                    es[generate_from].df[end])
                duration = (es[generate_from].df[end] -
                            es[generate_from].df[start]).dt.days
                duration = duration.tolist()
                es[self.target_entity].df[self.target_label] = duration
                updated_target_entity = es[self.target_entity].df
                duration_df = pd.DataFrame({'object_id': duration})

                es = es.entity_from_dataframe(
                    entity_id='Duration',
                    dataframe=duration_df,
                    index='object_id')

                es = es.entity_from_dataframe(entity_id=self.target_entity,
                                              dataframe=updated_target_entity,
                                              index='identifier')
                new_relationship = ft.Relationship(es['Duration']['object_id'],
                                                   es[self.target_entity][self.target_label])
                es = es.add_relationship(new_relationship)

                return es

            else:
                raise ValueError(
                    'Can not generate target label {} in table {}' +
                    'beacuse start or end labels in table {} contain missing value.'
                    .format(self.target_label,
                            self.target_entity,
                            generate_from))

        else:
            raise ValueError(
                'Can not generate target label {} in table {}.'.format(
                    self.target_label,
                    self.target_entity))
