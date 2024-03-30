import json, sys
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

LOG_FILE_PATH = "/PATH_TO_LOG_FILES/"
GRAPH_PATH = "./graphs_cache/"


def draw_graph_to_compare_v2(first_block_to_draw, last_block_to_draw, datas, field_name):

    startTime = datetime.now()

    fig, ax1 = plt.subplots()
    print("draw graph for field:", field_name)
    for sim_mode_name, data in datas.items():
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [blockNum for blockNum in json_keys]

        # extract fields
        print("extract fields")
        x_values_list = []
        y_values_list = []
        label_list = []

        if field_name == "ReadNums_TrieNode":
            # extract values
            try:
                y_values = [block_data["ReadTypes"]["trieNode"] if "trieNode" in block_data["ReadTypes"] else 0 for block_data in data.values()]
            except:
                y_values = [block_data["ReadNumsPerType"]["trieNode"] if "trieNode" in block_data["ReadNumsPerType"] else 0 for block_data in data.values()]
            x_values = [block_data["EndBlockNum"] for block_data in data.values()]

            # select values to draw graph
            measureInterval = x_values[1] - x_values[0]
            firstIndex = x_values.index(first_block_to_draw+measureInterval)
            lastIndex = x_values.index(last_block_to_draw)
            y_values = y_values[firstIndex:lastIndex+1]
            x_values = x_values[firstIndex:lastIndex+1]

            print("  mode:", sim_mode_name)
            print("  -> total trie node read num:", sum(y_values))

            # add values to draw graph
            x_values_list.append(x_values)
            y_values_list.append(np.cumsum(y_values))
            label_list.append(sim_mode_name)
        
        elif field_name == "ReadTimes_TrieNode":
            # extract values
            y_values = [block_data["ReadTimesPerType"]["trieNode"] if "trieNode" in block_data["ReadTimesPerType"] else 0 for block_data in data.values()]
            x_values = [block_data["EndBlockNum"] for block_data in data.values()]

            # select values to draw graph
            measureInterval = x_values[1] - x_values[0]
            firstIndex = x_values.index(first_block_to_draw+measureInterval)
            lastIndex = x_values.index(last_block_to_draw)
            y_values = y_values[firstIndex:lastIndex+1]
            x_values = x_values[firstIndex:lastIndex+1]

            print("  mode:", sim_mode_name)
            print("  -> total trie node read time:", sum(y_values), "ns")

            # add values to draw graph
            x_values_list.append(x_values)
            y_values_list.append(np.cumsum(y_values))
            label_list.append(sim_mode_name)
        
        elif field_name == "AvgReadTimes_TrieNode":
            # extract values
            y_values_time = [block_data["ReadTimesPerType"]["trieNode"] if "trieNode" in block_data["ReadTimesPerType"] else 0 for block_data in data.values()]
            try:
                y_values_num = [block_data["ReadTypes"]["trieNode"] if "trieNode" in block_data["ReadTypes"] else 0 for block_data in data.values()]
            except:
                y_values_num = [block_data["ReadNumsPerType"]["trieNode"] if "trieNode" in block_data["ReadNumsPerType"] else 0 for block_data in data.values()]
            x_values = [block_data["EndBlockNum"] for block_data in data.values()]

            print("  mode:", sim_mode_name)
            print("  -> avg trie node read time:", sum(y_values_time)/sum(y_values_num), "ns")
            
            # select values to draw graph
            measureInterval = x_values[1] - x_values[0]
            firstIndex = x_values.index(first_block_to_draw+measureInterval)
            lastIndex = x_values.index(last_block_to_draw)
            x_values = x_values[firstIndex:lastIndex+1]
            y_values_time = y_values_time[firstIndex:lastIndex+1]
            y_values_num = y_values_num[firstIndex:lastIndex+1]

            # batching values
            blockNums = x_values
            x_values = []
            y_values = []
            batch_size = 10
            for i in range(0, len(blockNums), batch_size):
                x_values.append(blockNums[i+batch_size-1])
                if sum(y_values_num[i:i+batch_size]) != 0:
                    y_values.append(sum(y_values_time[i:i+batch_size])/sum(y_values_num[i:i+batch_size]))
                else:
                    y_values.append(0)

            # add values to draw graph
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)
                
        elif field_name == "AvgReadLevels":
            try:
                y_values = [block_data["ReadNumsPerPosition"] for block_data in data.values()]
            except:
                y_values = [block_data["ReadPositions"] for block_data in data.values()]
            x_values = [block_data["EndBlockNum"] for block_data in data.values()]

            total_levels = []
            total_nums = []
            for y_value in y_values:
                total_level = 0
                total_num = 0
                for level, num in y_value.items():
                    if level == "disk_notFound" or level == "disk_unknown":
                        continue

                    total_num += num
                    if level[:4] == "disk":
                        level_int = int(level.split('_')[1])
                        total_level += (level_int+1)*num
                    else:
                        # level = "memory"
                        # memory's level is counted as 0, so just pass
                        pass
                total_levels.append(total_level)
                total_nums.append(total_num)

            # select values to draw graph
            measureInterval = x_values[1] - x_values[0]
            firstIndex = x_values.index(first_block_to_draw+measureInterval)
            lastIndex = x_values.index(last_block_to_draw)
            total_levels = total_levels[firstIndex:lastIndex+1]
            total_nums = total_nums[firstIndex:lastIndex+1]
            x_values = x_values[firstIndex:lastIndex+1]
            print("  mode:", sim_mode_name)
            print("  -> avg trie node read level:", sum(total_levels)/sum(total_nums), "(level n is counted as n+1)")

            # batching values
            blockNums = x_values
            x_values = []
            y_values = []
            batch_size = 10
            for i in range(0, len(blockNums), batch_size):
                x_values.append(blockNums[i+batch_size-1])
                if sum(total_nums[i:i+batch_size]) != 0:
                    y_values.append(sum(total_levels[i:i+batch_size])/sum(total_nums[i:i+batch_size]))
                else:
                    y_values.append(0)

            # add values to draw graph
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)

        else:
            print("not matching field name -> field name:", file_name)
            return

        # draw lines
        for i in range(len(x_values_list)):
            ax1.plot(x_values_list[i], y_values_list[i], marker='o', markersize=2, label=label_list[i])

            # print values
            # print("label:", label_list[i])
            # print("x values:", x_values_list[i])
            # print("y values:", y_values_list[i])
            # print("\n")

        # set axis
        ax1.set_xlabel('Block Number')
        ax1.set_ylabel(field_name)
        ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
    plt.title(field_name)
    plt.legend()

    file_name = field_name + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png'
    plt.savefig(GRAPH_PATH + file_name)

    print("finish analyze, file name:", file_name)
    print("elapsed time:", datetime.now()-startTime)


def graph_stack_graph(first_block_to_draw, last_block_to_draw, datas, field_name):

    startTime = datetime.now()

    max_top_y_value = 0
    y_values_to_stack = {}
    for sim_mode_name, data in datas.items():

        y_values_to_stack[sim_mode_name] = [[], []]

        if field_name == "ReadTimesPerPosition":
            ReadTimesPerPosition = [block_data['ReadTimesPerPosition'] for block_data in data.values()]
            all_keys = {}
            for i in ReadTimesPerPosition:
                keys = i.keys()
                for key in keys:
                    all_keys[key] = 0
            all_keys = list(all_keys.keys())
            all_keys.sort()

            blockNums = [block_data["EndBlockNum"] for block_data in data.values()]
            measureInterval = blockNums[1] - blockNums[0]
            firstIndex = blockNums.index(first_block_to_draw+measureInterval)
            lastIndex = blockNums.index(last_block_to_draw)
            blockNums = blockNums[firstIndex:lastIndex+1]

            top_y_value = 0
            for key in all_keys:
                values = [block_data["ReadTimesPerPosition"][key] if key in block_data["ReadTimesPerPosition"] else 0 for block_data in data.values()]
                values = values[firstIndex:lastIndex+1]
                y_values_to_stack[sim_mode_name][0].append(np.cumsum(values))
                y_values_to_stack[sim_mode_name][1].append(key)
                top_y_value += sum(values)
            if max_top_y_value < top_y_value:
                max_top_y_value = top_y_value

        elif field_name == "ReadTimesPerType":
            ReadTimesPerType = [block_data['ReadTimesPerType'] for block_data in data.values()]
            all_keys = {}
            for i in ReadTimesPerType:
                keys = i.keys()
                for key in keys:
                    all_keys[key] = 0
            all_keys = list(all_keys.keys())
            all_keys.sort()

            blockNums = [block_data["EndBlockNum"] for block_data in data.values()]
            measureInterval = blockNums[1] - blockNums[0]
            firstIndex = blockNums.index(first_block_to_draw+measureInterval)
            lastIndex = blockNums.index(last_block_to_draw)
            blockNums = blockNums[firstIndex:lastIndex+1]

            top_y_value = 0
            for key in all_keys:
                values = [block_data["ReadTimesPerType"][key] if key in block_data["ReadTimesPerType"] else 0 for block_data in data.values()]
                values = values[firstIndex:lastIndex+1]
                y_values_to_stack[sim_mode_name][0].append(np.cumsum(values))
                y_values_to_stack[sim_mode_name][1].append(key)
                top_y_value += sum(values)
            if max_top_y_value < top_y_value:
                max_top_y_value = top_y_value
        
        elif field_name == "ReadNumsPerPosition":
            try:
                ReadNumsPerPosition = [block_data['ReadNumsPerPosition'] for block_data in data.values()]
            except:
                ReadNumsPerPosition = [block_data['ReadPositions'] for block_data in data.values()]
            all_keys = {}
            for i in ReadNumsPerPosition:
                keys = i.keys()
                for key in keys:
                    all_keys[key] = 0
            all_keys = list(all_keys.keys())
            all_keys.sort()

            blockNums = [block_data["EndBlockNum"] for block_data in data.values()]
            measureInterval = blockNums[1] - blockNums[0]
            firstIndex = blockNums.index(first_block_to_draw+measureInterval)
            lastIndex = blockNums.index(last_block_to_draw)
            blockNums = blockNums[firstIndex:lastIndex+1]

            top_y_value = 0
            for key in all_keys:
                try:
                    values = [block_data["ReadNumsPerPosition"][key] if key in block_data["ReadNumsPerPosition"] else 0 for block_data in data.values()]
                except:
                    values = [block_data["ReadPositions"][key] if key in block_data["ReadPositions"] else 0 for block_data in data.values()]
                values = values[firstIndex:lastIndex+1]
                y_values_to_stack[sim_mode_name][0].append(np.cumsum(values))
                y_values_to_stack[sim_mode_name][1].append(key)
                top_y_value += sum(values)
            if max_top_y_value < top_y_value:
                max_top_y_value = top_y_value

        else:
            print("not matching field name:", field_name)
            return

    for sim_mode_name, _ in datas.items():
        
        fig, ax1 = plt.subplots()

        ax1.set_ylim(top=max_top_y_value) # set max y value

        print("draw graph")
        ax1.stackplot(blockNums, y_values_to_stack[sim_mode_name][0], labels=y_values_to_stack[sim_mode_name][1], alpha=0.5)

        ax1.set_xlabel('Block Number')
        ax1.set_ylabel(field_name)

        ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
        plt.title(field_name + "_" + sim_mode_name)
        # plt.legend(loc='upper left')
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles[::-1], labels[::-1], loc='upper left')

        plt.savefig(GRAPH_PATH + field_name + "_" + sim_mode_name + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png')

        print("elapsed time:", datetime.now()-startTime)
    
    print("finish analyze")
    print("total elapsed time:", datetime.now()-startTime)


def draw_graph_per_mode(first_block_to_draw, last_block_to_draw, datas, field_name):

    startTime = datetime.now()

    max_top_y_value = 0
    y_values_to_draw = {}
    for sim_mode_name, data in datas.items():

        y_values_to_draw[sim_mode_name] = [[], []]

        if field_name == "AvgReadTimesPerPosition":
            ReadTimesPerPosition = [block_data['ReadTimesPerPosition'] for block_data in data.values()]
            all_keys = {}
            for i in ReadTimesPerPosition:
                keys = i.keys()
                for key in keys:
                    all_keys[key] = 0
            all_keys = list(all_keys.keys())
            all_keys.sort()

            blockNums = [block_data["EndBlockNum"] for block_data in data.values()]
            measureInterval = blockNums[1] - blockNums[0]
            firstIndex = blockNums.index(first_block_to_draw+measureInterval)
            lastIndex = blockNums.index(last_block_to_draw)
            blockNums = blockNums[firstIndex:lastIndex+1]

            top_y_value = 0
            batch_size = 50
            for key in all_keys:
                times = [block_data["ReadTimesPerPosition"][key] if key in block_data["ReadTimesPerPosition"] else 0 for block_data in data.values()]
                try:
                    nums = [block_data["ReadNumsPerPosition"][key] if key in block_data["ReadNumsPerPosition"] else 0 for block_data in data.values()]
                except:
                    nums = [block_data["ReadPositions"][key] if key in block_data["ReadPositions"] else 0 for block_data in data.values()]
                times = times[firstIndex:lastIndex+1]
                nums = nums[firstIndex:lastIndex+1]

                # avg_times = [time/num if num != 0 else 0 for time, num in zip(times, nums)]
                # batching values
                y_values = []
                for i in range(0, len(blockNums), batch_size):
                    if sum(nums[i:i+batch_size]) != 0:
                        y_values.append(sum(times[i:i+batch_size])/sum(nums[i:i+batch_size]))
                    else:
                        y_values.append(0)
                avg_times = y_values

                y_values_to_draw[sim_mode_name][0].append(avg_times)
                y_values_to_draw[sim_mode_name][1].append(key)

                top_y_value = max(avg_times)
                if max_top_y_value < top_y_value:
                    max_top_y_value = top_y_value
            
            x_values = []
            for i in range(0, len(blockNums), batch_size):
                x_values.append(blockNums[i+batch_size-1])
            blockNums = x_values

        else:
            print("not matching field name:", field_name)
            return
        
    for sim_mode_name, _ in datas.items():
        
        fig, ax1 = plt.subplots()

        ax1.set_ylim(top=max_top_y_value) # set max y value

        print("draw graph")
        for i in range(len(y_values_to_draw[sim_mode_name][0])):
            ax1.plot(blockNums, y_values_to_draw[sim_mode_name][0][i], marker='o', markersize=2, label=y_values_to_draw[sim_mode_name][1][i])

        ax1.set_xlabel('Block Number')
        ax1.set_ylabel(field_name)

        ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
        plt.title(field_name + "_" + sim_mode_name)
        # plt.legend(loc='upper left')
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles[::-1], labels[::-1], loc='upper left')

        plt.savefig(GRAPH_PATH + field_name + "_" + sim_mode_name + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png')

        print("elapsed time:", datetime.now()-startTime)
    
    print("finish analyze")
    print("total elapsed time:", datetime.now()-startTime)


if __name__ == "__main__":

    startTime = datetime.now()
    
    # set simulation params
    startBlockNum = 0
    endBlockNum = 8000000
    deleteEpoch = 10
    inactivateEpoch = 10
    inactivateCriterion = 500000
    fromLevel = 0 # how many parent nodes to omit in Merkle proofs
    flushInterval = 1 # block flush interval (default: 1, at every block / but genesis block is always flushed)

    # graph options
    first_block_to_draw = 4000000
    last_block_to_draw = 8000000

    # collect log data
    datas = {}
    try:
        print("collect Ethereum data")
        sim_blocks_file_name = "cache_stats_Ethereum_" + str(startBlockNum) + "_" + str(endBlockNum) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['EthereumOS'] = data 
    except:
        print("  -> no EthereumOS data")
        sys.exit()

    try:
        print("collect Ethanos data")
        sim_blocks_file_name = "cache_stats_Ethanos_" + str(startBlockNum) + "_" + str(endBlockNum) + "_" + str(inactivateCriterion) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethanos'] = data 
    except:
        print("  -> no Ethanos data")
        sys.exit()

    try:
        print("collect Ethane data")
        sim_blocks_file_name = "cache_stats_Ethane_" + str(startBlockNum) + "_" + str(endBlockNum) + "_" + str(deleteEpoch) + "_" + str(inactivateEpoch) + "_" + str(inactivateCriterion) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethane'] = data 
    except:
        print("  -> no Ethane data")
        sys.exit()

    # select fields to draw graph
    field_names = ["ReadNums_TrieNode", "ReadTimes_TrieNode", "AvgReadTimes_TrieNode", 
                   "AvgReadLevels"]
    for field_name in field_names:
        print("field_name:", field_name)
        draw_graph_to_compare_v2(first_block_to_draw, last_block_to_draw, datas, field_name)
        print("\n\n\n")

    field_names = ["ReadTimesPerPosition", "ReadTimesPerType", "ReadNumsPerPosition"]
    for field_name in field_names:
        print("field_name:", field_name)
        graph_stack_graph(first_block_to_draw, last_block_to_draw, datas, field_name)
        print("\n\n\n")
    
    field_names = ["AvgReadTimesPerPosition"]
    for field_name in field_names:
        print("field_name:", field_name)
        draw_graph_per_mode(first_block_to_draw, last_block_to_draw, datas, field_name)
        print("\n\n\n")

    print("total elapsed time:", datetime.now()-startTime)
