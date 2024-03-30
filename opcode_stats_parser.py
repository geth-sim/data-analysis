import json, sys
from datetime import datetime
import matplotlib.pyplot as plt

LOG_FILE_PATH = "/PATH_TO_LOG_FILES/"
GRAPH_PATH = "./graphs_opcode/"


def extract_gas_per_sec_values(first_block_to_draw, last_block_to_draw, datas):

    startTime = datetime.now()

    fig, ax1 = plt.subplots()
    print("draw graph")
    for sim_mode_name, data in datas.items():
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [blockNum for blockNum in json_keys]

        # collect opcodeNums, opcodeExecutes, opcodeCosts
        totalOpcodeNums = dict()
        totalOpcodeExecutes = dict()
        totalOpcodeCosts = dict()        
        for blockNum in blockNums:
            if data[blockNum]["StartBlockNum"] < first_block_to_draw or data[blockNum]["EndBlockNum"] > last_block_to_draw:
                continue

            opcodeNums = data[blockNum]["OpcodeNums"]
            opcodeExecutes = data[blockNum]["OpcodeExecutes"]
            opcodeCosts = data[blockNum]["OpcodeCosts"]

            for opcodeName in opcodeNums:
                if not opcodeName in totalOpcodeNums:
                    totalOpcodeNums[opcodeName] = 0
                    totalOpcodeExecutes[opcodeName] = 0
                    totalOpcodeCosts[opcodeName] = 0

                totalOpcodeNums[opcodeName] += opcodeNums[opcodeName]
                totalOpcodeExecutes[opcodeName] += opcodeExecutes[opcodeName]
                totalOpcodeCosts[opcodeName] += opcodeCosts[opcodeName]

        # calculate gas/sec values
        totalOpcodeValues = dict()
        for opcodeName in totalOpcodeNums:
            print("for opcode", opcodeName)
            print("  nums:", totalOpcodeNums[opcodeName])
            print("  executes:", totalOpcodeExecutes[opcodeName])
            print("  costs:", totalOpcodeCosts[opcodeName])
            print("  =>", totalOpcodeCosts[opcodeName] / totalOpcodeExecutes[opcodeName], "gas/sec\n")
            totalOpcodeValues[opcodeName] = totalOpcodeCosts[opcodeName] / totalOpcodeExecutes[opcodeName]

        # save results
        file_name = 'result.json'
        with open(file_name, 'w') as fp:
            json.dump(totalOpcodeValues, fp, indent=4)
        print("save as json file:", file_name)


def draw_sec_per_gas_graphs(first_block_to_draw, last_block_to_draw, datas):

    startTime = datetime.now()
    
    print("draw graph")
    for sim_mode_name, data in datas.items():
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [blockNum for blockNum in json_keys]

        # collect opcodeNums, opcodeExecutes, opcodeCosts
        totalOpcodeNums = dict()
        totalOpcodeExecutes = dict()
        totalOpcodeCosts = dict()
        graph_values_per_opcode = dict()

        for blockNum in blockNums:
            if data[blockNum]["StartBlockNum"] < first_block_to_draw or data[blockNum]["EndBlockNum"] > last_block_to_draw:
                continue

            opcodeNums = data[blockNum]["OpcodeNums"]
            opcodeExecutes = data[blockNum]["OpcodeExecutes"]
            opcodeCosts = data[blockNum]["OpcodeCosts"]

            for opcodeName in opcodeNums:
                if not opcodeName in graph_values_per_opcode:
                    graph_values_per_opcode[opcodeName] = [[],[]]

                # gas_per_sec_value = opcodeCosts[opcodeName] / opcodeExecutes[opcodeName]
                sec_per_gas_value = opcodeExecutes[opcodeName] / opcodeCosts[opcodeName]
                graph_values_per_opcode[opcodeName][0].append(int(blockNum))
                graph_values_per_opcode[opcodeName][1].append(sec_per_gas_value)

                if not opcodeName in totalOpcodeNums:
                    totalOpcodeNums[opcodeName] = 0
                    totalOpcodeExecutes[opcodeName] = 0
                    totalOpcodeCosts[opcodeName] = 0

                totalOpcodeNums[opcodeName] += opcodeNums[opcodeName]
                totalOpcodeExecutes[opcodeName] += opcodeExecutes[opcodeName]
                totalOpcodeCosts[opcodeName] += opcodeCosts[opcodeName]

        total_sec_per_gas_values = dict()
        for opcodeName in totalOpcodeNums:
            total_sec_per_gas_values[opcodeName] = totalOpcodeExecutes[opcodeName]/totalOpcodeCosts[opcodeName]
        total_sec_per_gas_values = {k: v for k, v in sorted(total_sec_per_gas_values.items(), key=lambda item: item[1])}
        selected_opcodes = list(total_sec_per_gas_values.keys())
        selected_opcodes.reverse()
        opcode_num_to_draw = 10
        print("sorted opcodes:", selected_opcodes)
        print("total_sec_per_gas_values:", total_sec_per_gas_values)

        # draw graphs
        fig, ax1 = plt.subplots()
        # for opcodeName in graph_values_per_opcode:
        for opcodeName in selected_opcodes[:opcode_num_to_draw]:
            if opcodeName == "BLOCKHASH":
                continue

            x_values = graph_values_per_opcode[opcodeName][0]
            y_values = graph_values_per_opcode[opcodeName][1]

            ax1.plot(x_values, y_values, marker='o', markersize=2, label=opcodeName)

            # set axis
            ax1.set_xlabel('Block Number')
            ax1.set_ylabel("sec per gas")
            ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
        plt.title('sec per gas values for opcodes')
        plt.legend()

        file_name = 'gas_per_sec_values' + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png'
        plt.savefig(GRAPH_PATH + file_name)

    print("finish analyze, file name:", file_name)
    print("how many opcodes:", len(graph_values_per_opcode))
    print("elapsed time:", datetime.now()-startTime)


def draw_sec_per_gas_graphs_per_opcode(first_block_to_draw, last_block_to_draw, datas):

    startTime = datetime.now()
    
    print("draw graph")
    for sim_mode_name, data in datas.items():
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [blockNum for blockNum in json_keys]

        # collect opcodeNums, opcodeExecutes, opcodeCosts
        totalOpcodeNums = dict()
        totalOpcodeExecutes = dict()
        totalOpcodeCosts = dict()
        graph_values_per_opcode = dict()

        for blockNum in blockNums:
            if data[blockNum]["StartBlockNum"] < first_block_to_draw or data[blockNum]["EndBlockNum"] > last_block_to_draw:
                continue

            opcodeNums = data[blockNum]["OpcodeNums"]
            opcodeExecutes = data[blockNum]["OpcodeExecutes"]
            opcodeCosts = data[blockNum]["OpcodeCosts"]

            for opcodeName in opcodeNums:
                if not opcodeName in graph_values_per_opcode:
                    graph_values_per_opcode[opcodeName] = [[],[]]

                # gas_per_sec_value = opcodeCosts[opcodeName] / opcodeExecutes[opcodeName]
                sec_per_gas_value = opcodeExecutes[opcodeName] / opcodeCosts[opcodeName]
                graph_values_per_opcode[opcodeName][0].append(int(blockNum))
                graph_values_per_opcode[opcodeName][1].append(sec_per_gas_value)

                if not opcodeName in totalOpcodeNums:
                    totalOpcodeNums[opcodeName] = 0
                    totalOpcodeExecutes[opcodeName] = 0
                    totalOpcodeCosts[opcodeName] = 0

                totalOpcodeNums[opcodeName] += opcodeNums[opcodeName]
                totalOpcodeExecutes[opcodeName] += opcodeExecutes[opcodeName]
                totalOpcodeCosts[opcodeName] += opcodeCosts[opcodeName]

        total_sec_per_gas_values = dict()
        for opcodeName in totalOpcodeNums:
            total_sec_per_gas_values[opcodeName] = totalOpcodeExecutes[opcodeName]/totalOpcodeCosts[opcodeName]
        total_sec_per_gas_values = {k: v for k, v in sorted(total_sec_per_gas_values.items(), key=lambda item: item[1])}
        selected_opcodes = list(total_sec_per_gas_values.keys())
        selected_opcodes.reverse()
        print("sorted opcodes:", selected_opcodes)
        print("total_sec_per_gas_values:", total_sec_per_gas_values)

        # draw graphs
        
        # for opcodeName in graph_values_per_opcode:
        for opcodeName in selected_opcodes:
            
            fig, ax1 = plt.subplots()

            x_values = graph_values_per_opcode[opcodeName][0]
            y_values = graph_values_per_opcode[opcodeName][1]

            # ax1.plot(x_values, y_values, marker='o', markersize=2, label=opcodeName)
            ax1.scatter(x_values, y_values, marker='o', s=1 ,label=opcodeName)

            # set axis
            ax1.set_xlabel('Block Number')
            ax1.set_ylabel("sec per gas")
            ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
            plt.title('sec per gas values for opcodes')
            plt.legend()

            file_name = 'gas_per_sec_values_' + opcodeName + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png'
            plt.savefig(GRAPH_PATH + file_name)
            print("save graph:", file_name)
    
    print("how many opcodes:", len(graph_values_per_opcode))
    print("elapsed time:", datetime.now()-startTime)


def change_log_epoch_length(datas, log_epoch_len):
    startTime = datetime.now()
    
    print("draw graph")
    
    for sim_mode_name, data in datas.items():
        before_len = len(data)
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [blockNum for blockNum in json_keys]

        current_log_epoch_len = int(blockNums[1]) - int(blockNums[0])

        if current_log_epoch_len == log_epoch_len:
            print("already has target log epoch len")
            return
        
        index = 0
        while True:
                        
            if index+1 < len(data):
                # print("key:", blockNums[index])
                left_opcode_stats = data[blockNums[index]]
                right_opcode_stats = data[blockNums[index+1]]

                print(left_opcode_stats["EndBlockNum"], left_opcode_stats["StartBlockNum"], left_opcode_stats["EndBlockNum"] - left_opcode_stats["StartBlockNum"]+1)

                if left_opcode_stats["EndBlockNum"] - left_opcode_stats["StartBlockNum"] == log_epoch_len:
                    print("\ngo to next stats")
                    index += 1
                    continue
                elif left_opcode_stats["EndBlockNum"] - left_opcode_stats["StartBlockNum"] + 1 == log_epoch_len:
                    print("\ngo to next stats")
                    index += 1
                    continue
                else:
                    print("\n->", left_opcode_stats["EndBlockNum"] - left_opcode_stats["StartBlockNum"]+1)
                    print("add", blockNums[index], blockNums[index+1])
                    right_opcode_stats["StartBlockNum"] = left_opcode_stats["StartBlockNum"]
                    right_opcode_stats["ContractCallNum"] += left_opcode_stats["ContractCallNum"]

                    if left_opcode_stats["OpcodeNums"] != None:
                        for opcodeName in left_opcode_stats["OpcodeNums"]:
                            if not opcodeName in right_opcode_stats["OpcodeNums"]:
                                right_opcode_stats["OpcodeNums"][opcodeName] = 0
                                right_opcode_stats["OpcodeExecutes"][opcodeName] = 0
                                right_opcode_stats["OpcodeCosts"][opcodeName] = 0
                            
                            right_opcode_stats["OpcodeNums"][opcodeName] += left_opcode_stats["OpcodeNums"][opcodeName]
                            right_opcode_stats["OpcodeExecutes"][opcodeName] += left_opcode_stats["OpcodeExecutes"][opcodeName]
                            right_opcode_stats["OpcodeCosts"][opcodeName] += left_opcode_stats["OpcodeCosts"][opcodeName]

                    del data[blockNums[index]]
                    json_keys = list(data.keys())
                    blockNums = [blockNum for blockNum in json_keys]
            else:
                break
        
        print("before len:", before_len)
        print("after len:", len(data))

        # save results
        # file_name = 'change_epoch.json'
        # with open(file_name, 'w') as fp:
        #     json.dump(data, fp, indent=4)
        # print("save as json file:", file_name)


if __name__ == "__main__":

    startTime = datetime.now()
    
    # set simulation params
    startBlockNum = 0
    endBlockNum = 10000000
    fromLevel = 0 # how many parent nodes to omit in Merkle proofs
    flushInterval = 1 # block flush interval (default: 1, at every block / but genesis block is always flushed)

    # graph options
    first_block_to_draw = startBlockNum
    last_block_to_draw = endBlockNum
    graph_window_size = 100000
    log_epoch_len = 10000

    # collect log data
    datas = {}

    try:
        print("collect Ethereum opcode data")
        opcode_stats_file_name = "opcode_stats_Ethereum_" + str(startBlockNum) + "_" + str(endBlockNum) + ".json"
        print("  file name:", opcode_stats_file_name)
        with open(LOG_FILE_PATH+opcode_stats_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethereum'] = data 
    except:
        print("  -> no Ethereum data")
        sys.exit()
    
    change_log_epoch_length(datas, log_epoch_len)

    extract_gas_per_sec_values(first_block_to_draw, last_block_to_draw, datas)
    draw_sec_per_gas_graphs(first_block_to_draw, last_block_to_draw, datas)
    draw_sec_per_gas_graphs_per_opcode(first_block_to_draw, last_block_to_draw, datas)

    print("total elapsed time:", datetime.now()-startTime)
