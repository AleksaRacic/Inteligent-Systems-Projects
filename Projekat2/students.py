import random

from agents import Agent


# Example agent, behaves randomly.
# ONLY StudentAgent and his descendants have a 0 id. ONLY one agent of this type must be present in a game.
# Agents from bots.py have successive ids in a range from 1 to number_of_bots.
class StudentAgent(Agent):
    def __init__(self, position, file_name):
        super().__init__(position, file_name)
        self.id = 0

    @staticmethod
    def kind():
        return '0'

    # Student shall override this method in derived classes.
    # This method should return one of the legal actions (from the Actions class) for the current state.
    # state - represents a state object.
    # max_levels - maximum depth in a tree search. If max_levels eq -1 than the tree search depth is unlimited.
    def get_next_action(self, state, max_levels):
        actions = self.get_legal_actions(state)  # equivalent of state.get_legal_actions(self.id)
        chosen_action = actions[random.randint(0, len(actions) - 1)]
        # Example of a new_state creation (for a chosen_action of a self.id agent):
        # new_state = state.apply_action(self.id, chosen_action)
        return chosen_action



class MinimaxAgent(StudentAgent):
    def __init__(self, position, file_name):
        super().__init__(position, file_name)
        self.max_levels = -1
    
    def __minmax(self, state, current_level, agent_id):
        state.adjust_win_loss()
        if state.is_win():
            if self.id == 0:
                return 1, []
            else:
                return -1, []

        elif state.is_loss():
            if self.id == 0:
                return -1, []
            else:
                return 1, []
        
        if not self.max_levels == -1 and current_level == self.max_levels:
            return 0, []

        is_max = agent_id == self.id
        best_action_val = -2 if is_max else 2
        actions_list = []

        for action in state.get_legal_actions(agent_id):
            new_state = state.apply_action(agent_id, action)
            action_val, _ = self.__minmax(new_state, current_level + 1, (agent_id + 1) % 2)

            if best_action_val == action_val:
                actions_list.append(action)

            if is_max and best_action_val < action_val:
                best_action_val = action_val
                actions_list = []
                actions_list.append(action)
            
            if (not is_max) and best_action_val > action_val:
                best_action_val = action_val
                actions_list = []
        
        #print(f"Best action val: {best_action_val} Action list: {actions_list} Level AgentId: {agent_id} \n")
        #print(state.char_map, "\n\n")

        return best_action_val, actions_list

    def get_next_action(self, state, max_levels):
        if len(state.agents) != 2:
            raise Exception("Student mora imati jednog protivnika")
        self.max_levels = max_levels

        val, actions = self.__minmax(state, self.id, 0)
        #print(f"Agent {self.id}: potezi {actions}, sa vrednoscu {val}")
        return actions[0]





class MinimaxABAgent(StudentAgent):
    def __init__(self, position, file_name):
        super().__init__(position, file_name)
        self.max_levels = -1

    def __minmaxAB(self, state, current_level, agent_id, alpha, beta):
        state.adjust_win_loss()
        if state.is_win():
            if self.id == 0:
                return 1, []
            else:
                return -1, []

        elif state.is_loss():
            if self.id == 0:
                return -1, []
            else:
                return 1, []
        
        if not self.max_levels == -1 and current_level == self.max_levels:
            return 0, []

        is_max = agent_id == self.id
        best_action_val = -1 if is_max else 1
        actions_list = []

        for action in state.get_legal_actions(agent_id):
            new_state = state.apply_action(agent_id, action)
            action_val, _ = self.__minmaxAB(new_state, current_level + 1, (agent_id + 1) % 2, alpha, beta)

            if best_action_val == action_val:
                actions_list.append(action)

            if is_max and best_action_val < action_val:
                best_action_val = action_val
                actions_list = []
                actions_list.append(action)
                alpha = max(alpha, best_action_val)
                if beta <= alpha:
                    break
            
            if (not is_max) and best_action_val > action_val:
                best_action_val = action_val
                actions_list = []
                beta = min(beta, best_action_val)
                if beta <= alpha:
                    break
        
        #print(f"Best action val: {best_action_val} Action list: {actions_list} Level AgentId: {agent_id} \n")
        #print(state.char_map, "\n\n")

        return best_action_val, actions_list

    def get_next_action(self, state, max_levels):
        if len(state.agents) != 2:
            raise Exception("Student mora imati jednog protivnika")
        self.max_levels = max_levels

        val, actions = self.__minmaxAB(state, 0, self.id, -2, 2)
        #print(f"Agent {self.id}: potezi {actions}, sa vrednoscu {val}")
        return actions[0]


class ExpectAgent(StudentAgent):
    def __init__(self, position, file_name):
        super().__init__(position, file_name)
        self.max_levels = -1
    
    def __expectimax(self, state, current_level, agent_id):
        state.adjust_win_loss()
        if state.is_win():
            if self.id == 0:
                return 1, []
            else:
                return -1, []

        elif state.is_loss():
            if self.id == 0:
                return -1, []
            else:
                return 1, []
        
        if not self.max_levels == -1 and current_level == self.max_levels:
            return 0, []

        is_max = agent_id == self.id
        if is_max:
            best_action_val = -2 if is_max else 2
        else:
            best_action_val = 0
        actions_list = []
        print(state.char_map, "\n\n")
        actions = state.get_legal_actions(agent_id)
        probability = 1/len(actions)
        for action in actions:
            new_state = state.apply_action(agent_id, action)
            action_val, _ = self.__expectimax(new_state, current_level + 1, (agent_id + 1) % 2)

            if best_action_val == action_val:
                actions_list.append(action)

            if is_max and best_action_val < action_val:
                best_action_val = action_val
                actions_list = []
                actions_list.append(action)
            
            if (not is_max):
                best_action_val += probability * action_val
        
        #print(f"Best action val: {best_action_val} Action list: {actions_list} Level AgentId: {agent_id} \n")
        #print(state.char_map, "\n\n")

        return best_action_val, actions_list

    def get_next_action(self, state, max_levels):
        if len(state.agents) != 2:
            raise Exception("Student mora imati jednog protivnika")
        self.max_levels = max_levels

        val, actions = self.__expectimax(state, self.id, 0)
        #print(f"Agent {self.id}: potezi {actions}, sa vrednoscu {val}")
        return actions[0]

class MaxNAgent(StudentAgent):
    def __init__(self, position, file_name):
        super().__init__(position, file_name)
        self.max_levels = -1

    def __minmaxNAB(self, state, current_level, agent_id, alpha, beta):
        if state.is_agent_win(self.id):
            return 1, []
        elif state.is_agent_loss(self.id):
            return -1, []
        
        if not self.max_levels == -1 and current_level == self.max_levels:
            return 0, []

        is_max = agent_id == self.id
        best_action_val = -2 if is_max else 2
        actions_list = []
        actions = state.get_legal_actions(agent_id)

        if len(actions) == 0:
            action_val, _ = self.__minmaxNAB(state, current_level + 1, (agent_id + 1) % len(state.agents), alpha, beta)
        else:
            for action in actions:
                new_state = state.apply_action(agent_id, action)
                action_val, _ = self.__minmaxNAB(new_state, current_level + 1, (agent_id + 1) % len(state.agents), alpha, beta)

                if best_action_val == action_val:
                    actions_list.append(action)

                if is_max and best_action_val < action_val:
                    best_action_val = action_val
                    actions_list = []
                    actions_list.append(action)
                    alpha = max(alpha, best_action_val)
                    if beta <= alpha:
                        break
                
                if (not is_max) and best_action_val > action_val:
                    best_action_val = action_val
                    actions_list = []
                    beta = min(beta, best_action_val)
                    if beta <= alpha:
                        break
        
        #print(f"Best action val: {best_action_val} Action list: {actions_list} Level AgentId: {agent_id} \n")
        #print(state.char_map, "\n\n")

        return best_action_val, actions_list

    def get_next_action(self, state, max_levels):
        self.max_levels = max_levels

        val, actions = self.__minmaxNAB(state, 0, self.id, -3, 3)
        #print(f"Agent {self.id}: potezi {actions}, sa vrednoscu {val}")
        return actions[0]
