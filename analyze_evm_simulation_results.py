import json, sys
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bisect
from statistics import median

LOG_FILE_PATH = "/PATH_TO_LOG_FILES/"
GRAPH_PATH = "./graphs/"


def draw_graph_to_compare_v2(startBlockNum, endBlockNum, first_block_to_draw, last_block_to_draw, batch_size, datas, field_name):

    startTime = datetime.now()

    fig, ax1 = plt.subplots()
    print("draw graph")
    for sim_mode_name, data in datas.items():
        
        # extract block nums
        json_keys = list(data.keys())
        blockNums = [int(blockNum) for blockNum in json_keys]

        # extract fields
        print("extract fields")
        x_values_list = []
        y_values_list = []
        label_list = []
        if field_name == "PaymentTxAvgExecute":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            PaymentTxExecutes = [block_data['PaymentTxExecutes'] for block_data in data.values()]

            x_values = []
            y_values = []
            for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                tx_len_sum = sum(PaymentTxLen[i-batch_size:i])
                if tx_len_sum != 0:
                    x_values.append(i)
                    y_values.append(sum(PaymentTxExecutes[i-batch_size:i])/tx_len_sum)

            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)

        elif field_name == "CallTxAvgExecute":
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            CallTxExecutes = [block_data['CallTxExecutes'] for block_data in data.values()]

            x_values = []
            y_values = []
            for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                tx_len_sum = sum(CallTxLen[i-batch_size:i])
                if tx_len_sum != 0:
                    x_values.append(i)
                    y_values.append(sum(CallTxExecutes[i-batch_size:i])/tx_len_sum)
                
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)
            
        elif field_name == "TotalTxAvgExecute":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            PaymentTxExecutes = [block_data['PaymentTxExecutes'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            CallTxExecutes = [block_data['CallTxExecutes'] for block_data in data.values()]
            
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]
            TxExecutes = [paymentExecutes + callExecutes for paymentExecutes, callExecutes in zip(PaymentTxExecutes, CallTxExecutes)]

            if sim_mode_name[:6] == "Ethane":
                # ethane with void reads and without delete & inactivate overhead
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithVoidReads&WithoutDelete&Inactivate")

                # actual tx execute time without void reads
                sum1 = sum(TxExecutes)
                VoidAccountReads = [block_data['VoidAccountReads'] for block_data in data.values()]
                TxExecutes = [te - var for te, var in zip(TxExecutes, VoidAccountReads)]
                sum2 = sum(TxExecutes)
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithoutVoidReads&Delete&Inactivate")

                # tx execute time including deletion and inactivation
                DeleteUpdates = [block_data['DeleteUpdates'] for block_data in data.values()]
                InactivateUpdates = [block_data['InactivateUpdates'] for block_data in data.values()]
                InactivateHashes = [block_data['InactivateHashes'] for block_data in data.values()]
                UsedProofUpdtaes = [block_data['UsedProofUpdtaes'] for block_data in data.values()]
                TxExecutes = [te + du + iu + ih + upd for te, du, iu, ih, upd in zip(TxExecutes, DeleteUpdates, InactivateUpdates, InactivateHashes, UsedProofUpdtaes)]
                sum3 = sum(TxExecutes)

                print("sum1:", sum1, "sum2:", sum2, "sum3:", sum3)
                print("ethane's additional overhead per tx:", (sum3-sum2)/sum2*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

            elif sim_mode_name[:7] == "Ethanos":
                # ethanos tx execute time
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)

                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

                # if cached trie has snapshot or utilize bloom filter
                # cached trie read time can be removed
                CachedAccountReads = [block_data['CachedAccountReads'] for block_data in data.values()]
                sum1 = sum(TxExecutes)
                TxExecutes = [te - car for te, car in zip(TxExecutes, CachedAccountReads)]
                sum2 = sum(TxExecutes)
                print("sum1:", sum1, "sum2:", sum2)
                print("ethanos tx performance without cached trie reads:", (sum1-sum2)/sum1*100, "%")
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithoutCachedTrieReads")

            else:
                # ethereum tx execute time
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TxExecutes[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

        elif field_name == "AvgReadPerTx":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            AccountReads = [block_data['AccountReads'] for block_data in data.values()]
            SnapshotAccountReads = [block_data['SnapshotAccountReads'] for block_data in data.values()]
            if sum(AccountReads) == 0:
                AccountReads = SnapshotAccountReads
            else:
                if sum(SnapshotAccountReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for account")
                    sys.exit()
            StorageReads = [block_data['StorageReads'] for block_data in data.values()]
            SnapshotStorageReads = [block_data['SnapshotStorageReads'] for block_data in data.values()]
            if sum(StorageReads) == 0:
                StorageReads = SnapshotStorageReads
            else:
                if sum(SnapshotStorageReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for storage")
                    sys.exit()
            TotalReads = [x + y for x, y in zip(AccountReads, StorageReads)]

            if sim_mode_name[:6] == "Ethane":
                # add active index read time (K_A)
                sum0 = sum(TotalReads)
                try:
                    ActiveIndexReads = [block_data['ActiveIndexReads'] for block_data in data.values()]
                except:
                    ActiveIndexReads = [0]*len(TotalReads)
                TotalReads = [x + y for x, y in zip(TotalReads, ActiveIndexReads)]
                sum1 = sum(TotalReads)
                print("sum0:", sum0, "sum1:", sum1)
                print("ethane's active index read time percentage of total reads:", sum(ActiveIndexReads)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TotalReads[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithVoidReads")

                # actual tx execute time without void reads
                VoidAccountReads = [block_data['VoidAccountReads'] for block_data in data.values()]
                TotalReads = [te - var for te, var in zip(TotalReads, VoidAccountReads)]
                sum2 = sum(TotalReads)
                print("sum1:", sum1, "sum2:", sum2)
                print("ethane all reads without void reads:", (sum1-sum2)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TotalReads[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

            elif sim_mode_name[:7] == "Ethanos":
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TotalReads[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

                # ethanos without cached trie reads
                CachedAccountReads = [block_data['CachedAccountReads'] for block_data in data.values()]
                sum1 = sum(TotalReads)
                TotalReads = [te - car for te, car in zip(TotalReads, CachedAccountReads)]
                sum2 = sum(TotalReads)
                print("sum1:", sum1, "sum2:", sum2)
                print("ethanos all reads without cached trie reads:", (sum1-sum2)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TotalReads[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithoutCachedTrieReads")

            else:
                # ethereum
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(TotalReads[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

        elif field_name == "AvgAccountReadPerTx":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            AccountReads = [block_data['AccountReads'] for block_data in data.values()]
            SnapshotAccountReads = [block_data['SnapshotAccountReads'] for block_data in data.values()]
            if sum(AccountReads) == 0:
                AccountReads = SnapshotAccountReads
            else:
                if sum(SnapshotAccountReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for account")
                    sys.exit()

            if sim_mode_name[:6] == "Ethane":
                # add active index read time (K_A)
                sum0 = sum(AccountReads)
                try:
                    ActiveIndexReads = [block_data['ActiveIndexReads'] for block_data in data.values()]
                except:
                    ActiveIndexReads = [0]*len(AccountReads)
                AccountReads = [x + y for x, y in zip(AccountReads, ActiveIndexReads)]
                sum1 = sum(AccountReads)
                print("sum0:", sum0, "sum1:", sum1)
                print("ethane's active index read time percentage of account reads:", sum(ActiveIndexReads)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(AccountReads[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithVoidReads")

                # actual tx execute time without void reads
                VoidAccountReads = [block_data['VoidAccountReads'] for block_data in data.values()]
                AccountReads = [te - var for te, var in zip(AccountReads, VoidAccountReads)]
                sum2 = sum(AccountReads)
                print("sum1:", sum1, "sum2:", sum2)
                print("ethane account reads without void reads:", (sum1-sum2)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(AccountReads[i-batch_size:i])/tx_len_sum)

                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

            elif sim_mode_name[:7] == "Ethanos":

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(AccountReads[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

                CachedAccountReads = [block_data['CachedAccountReads'] for block_data in data.values()]
                sum1 = sum(AccountReads)
                AccountReads = [te - car for te, car in zip(AccountReads, CachedAccountReads)]
                sum2 = sum(AccountReads)
                print("sum1:", sum1, "sum2:", sum2)
                print("ethanos account reads without cached trie reads:", (sum1-sum2)/sum1*100, "%")

                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(AccountReads[i-batch_size:i])/tx_len_sum)
                # x_values_list.append(x_values)
                # y_values_list.append(y_values)
                # label_list.append(sim_mode_name+"WithoutCachedTrieReads")
            
            else:
                x_values = []
                y_values = []
                for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                    tx_len_sum = sum(TxLen[i-batch_size:i])
                    if tx_len_sum != 0:
                        x_values.append(i)
                        y_values.append(sum(AccountReads[i-batch_size:i])/tx_len_sum)
                x_values_list.append(x_values)
                y_values_list.append(y_values)
                label_list.append(sim_mode_name)

        elif field_name == "AvgStorageReadPerTx":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            StorageReads = [block_data['StorageReads'] for block_data in data.values()]
            SnapshotStorageReads = [block_data['SnapshotStorageReads'] for block_data in data.values()]
            if sum(StorageReads) == 0:
                StorageReads = SnapshotStorageReads
            else:
                if sum(SnapshotStorageReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for storage")
                    sys.exit()

            x_values = []
            y_values = []
            for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                tx_len_sum = sum(TxLen[i-batch_size:i])
                if tx_len_sum != 0:
                    x_values.append(i)
                    y_values.append(sum(StorageReads[i-batch_size:i])/tx_len_sum)
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)
        
        elif field_name == "AvgCommitPerTx":
            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            AccountCommits = [block_data['AccountCommits'] for block_data in data.values()]
            StorageCommits = [block_data['StorageCommits'] for block_data in data.values()]
            SnapshotCommits = [block_data['SnapshotCommits'] for block_data in data.values()]
            TrieDBCommits = [block_data['TrieDBCommits'] for block_data in data.values()]
            DiskCommits = [block_data['DiskCommits'] for block_data in data.values()]
            TotalCommits = [a + b + c + d + e for a, b, c, d, e in zip(AccountCommits, StorageCommits, SnapshotCommits, TrieDBCommits, DiskCommits)]

            x_values = []
            y_values = []
            for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                tx_len_sum = sum(TxLen[i-batch_size:i])
                if tx_len_sum != 0:
                    x_values.append(i)
                    y_values.append(sum(TotalCommits[i-batch_size:i])/tx_len_sum)
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)
        
        elif field_name == "CumumlativeBlockExecuteTime":
            BlockExecuteTime = [block_data['BlockExecuteTime'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            blockNums = range(first_block_to_draw, last_block_to_draw+1)

            x_values_list.append(blockNums)
            y_values_list.append(np.cumsum(BlockExecuteTime))
            label_list.append(sim_mode_name)
        
        elif field_name == "AvgBlockExecute":
            BlockExecuteTime = [block_data['BlockExecuteTime'] for block_data in data.values()]

            x_values = []
            y_values = []
            for i in range(first_block_to_draw+batch_size, last_block_to_draw+1, batch_size):
                x_values.append(i)
                y_values.append(sum(BlockExecuteTime[i-batch_size:i])/batch_size)
            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)

        elif field_name == "DiskSize":

            batch_size = 1

            DiskSize = [block_data['DiskSize'] for block_data in data.values()]

            x_values = [index for index, size in enumerate(DiskSize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]
            y_values = [size for index, size in enumerate(DiskSize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]

            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)

            try:
                HistorySize = [block_data['HistorySize'] for block_data in data.values()]
                # path-based state scheme
                if sum(HistorySize) != 0:
                    # essential state data for state processing
                    StateSize = [totalSize - historySize for totalSize, historySize in zip(DiskSize, HistorySize)]
                    x_values = [index for index, size in enumerate(StateSize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]
                    y_values = [size for index, size in enumerate(StateSize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]
                    x_values_list.append(x_values)
                    y_values_list.append(y_values)
                    label_list.append(sim_mode_name+"_state")

                    # state history data for state rollback
                    x_values = [index for index, size in enumerate(HistorySize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]
                    y_values = [size for index, size in enumerate(HistorySize) if size != 0 and index >= first_block_to_draw and index <= last_block_to_draw ]
                    x_values_list.append(x_values)
                    y_values_list.append(y_values)
                    label_list.append(sim_mode_name+"_history")

            except:
                pass

        elif field_name == "EthaneOverheads":

            if sim_mode_name[:6] != "Ethane":
                continue
            
            print("sim mode:", sim_mode_name)
            blockNums = [int(blockNum) for blockNum in json_keys]

            DeleteUpdates = [block_data['DeleteUpdates'] for block_data in data.values()]
            DeleteHashes = [block_data['DeleteHashes'] for block_data in data.values()]
            DeleteNum = [block_data['DeleteNum'] for block_data in data.values()]

            InactivateUpdates = [block_data['InactivateUpdates'] for block_data in data.values()]
            UsedProofUpdtaes = [block_data['UsedProofUpdtaes'] for block_data in data.values()]
            InactivateHashes = [block_data['InactivateHashes'] for block_data in data.values()]
            InactivateNum = [block_data['InactivateNum'] for block_data in data.values()]
            UsedProofNum = [block_data['UsedProofNum'] for block_data in data.values()]

            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            PaymentTxExecutes = [block_data['PaymentTxExecutes'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            CallTxExecutes = [block_data['CallTxExecutes'] for block_data in data.values()]
            
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]
            TxExecutes = [paymentExecutes + callExecutes for paymentExecutes, callExecutes in zip(PaymentTxExecutes, CallTxExecutes)]

            #
            # draw latex box plot for Ethane's delete/inactivate execution time
            #

            divScale = 1000000 # (10^0: nanosecond, 10^3: microsecond, 10^6: millisecond, 10^9: second)
            
            DeleteTimes = [(x + y)/divScale for x, y in zip(DeleteUpdates, DeleteHashes)]
            InactivateTimes = [(x + y + z)/divScale for x, y, z in zip(InactivateUpdates, UsedProofUpdtaes, InactivateHashes)]

            drawTukeyStyle = False # remove outliers following Tukey style box plot
            removeExtremeOutliers = True # remove outliers over "outlierPercentage"
            outlierPercentage = 1 # %

            print("divScale:", divScale, "\n")
            print("outlierPercentage:", outlierPercentage, "\n")
            for i in range(0, blockNums[-1], inactivateCriterion):
                print("\t% => at round", int(1 + i/inactivateCriterion))

                subTxLen = TxLen[i:i+inactivateCriterion]
                subTxExecutes = TxExecutes[i:i+inactivateCriterion]

                txExecutesSum = sum(subTxExecutes)/divScale
                txLenSum = sum(subTxLen)
                deleteTimeSum = sum(DeleteTimes[i:i+inactivateCriterion])
                deleteCnt = len([x for x in DeleteTimes[i:i+inactivateCriterion] if x != 0])
                inactivateTimeSum = sum(InactivateTimes[i:i+inactivateCriterion])
                inactivateCnt = len([x for x in InactivateTimes[i:i+inactivateCriterion] if x != 0])
                if inactivateCnt==0:
                    inactivateCnt=1

                print("\t% total tx execute time:", txExecutesSum, ", total tx num:", txLenSum, ", avg tx execute time:", txExecutesSum/txLenSum)
                print("\t% total delete tme:", deleteTimeSum, ", delete cnt:", deleteCnt, ", avg delete time:", deleteTimeSum/deleteCnt, ", delete/txExecute percentage:", deleteTimeSum/txExecutesSum*100, "%")
                print("\t% total inactivate time:", inactivateTimeSum, ", inactivate cnt:", inactivateCnt, ", avg inactivate time:", inactivateTimeSum/inactivateCnt, ", inactivate/txExecute percentage:", inactivateTimeSum/txExecutesSum*100, "%")

                listsToDrawBoxPlot = [DeleteTimes[i:i+inactivateCriterion], InactivateTimes[i:i+inactivateCriterion]]
                for myList in listsToDrawBoxPlot:

                    myList = [x for x in myList if x != 0]
                    if len(myList) == 0:
                        print("\t\\addplot+ [boxplot prepared={")
                        print("\t\tlower whisker=", 0, ", lower quartile=", 0, \
                            ", median=", 0, ", upper quartile=", 0, ", upper whisker=", 0)
                        print("\t}] coordinates {};")
                        continue

                    q1 = np.percentile(myList, 25)
                    med = median(myList)
                    q3 = np.percentile(myList, 75)
                    iqr = q3 - q1

                    # remove outliters ()
                    myList.sort()
                    realMin = myList[0]
                    realMax = myList[-1]
                    myListLenWithOutliers = len(myList)
                    if drawTukeyStyle:
                        myList = [x for x in myList if x >= q1 - 1.5*iqr and x <= q3 + 1.5*iqr]
                    elif removeExtremeOutliers:
                        outlierNum = int(len(myList)*outlierPercentage/100)
                        myList = myList[0:-outlierNum]
                    print("\t% outliers num:", myListLenWithOutliers - len(myList))
                    lowerWhisker = myList[0]
                    upperWhisker = myList[-1]

                    print("\t\\addplot+ [boxplot prepared={")
                    print("\t\tlower whisker=", round(lowerWhisker, 2), ", lower quartile=", round(q1, 2), \
                        ", median=", round(med, 2), ", upper quartile=", round(q3, 2), ", upper whisker=", round(upperWhisker, 2))
                    print("\t}] coordinates {};")
                    print("\t% => realMin:", realMin, "/ realMax:", realMax)
                print("\t\\addplot+ [boxplot prepared={}] coordinates {};")
                print("")

            #
            # delete previous account time
            #
                
            DeleteUpdates = [block_data['DeleteUpdates'] for block_data in data.values()]
            DeleteHashes = [block_data['DeleteHashes'] for block_data in data.values()]
            
            DeleteTimes = [x + y for x, y in zip(DeleteUpdates, DeleteHashes)]
            blockNums = [int(blockNum) for blockNum in json_keys]

            print("box plot for Ethane's delete time overhead")
            boxPlots = []
            divScale = 1000000 # (10^3: microsecond, 10^6: millisecond, 10^9: second)
            print("divScale:", divScale, "\n")
            for i in range(0, blockNums[-1], inactivateCriterion):
                myList = [x for x in DeleteTimes[i:i+inactivateCriterion] if x != 0]

                q1 = np.percentile(myList, 25)
                med = median(myList)
                q3 = np.percentile(myList, 75)
                iqr = q3 - q1

                myListWithoutOutliers = [x for x in myList if x >= q1 - 1.5*iqr]
                myListWithoutOutliers.sort()
                lowerWhisker = myListWithoutOutliers[0]

                myListWithoutOutliers = [x for x in myList if x <= q3 + 1.5*iqr]
                myListWithoutOutliers.sort()
                upperWhisker = myListWithoutOutliers[-1]
                
                print("\t% => at round", int(1 + i/inactivateCriterion))
                print("\t\\addplot+ [boxplot prepared={")
                print("\t\tlower whisker=", round(lowerWhisker/divScale, 2), ", lower quartile=", round(q1/divScale, 2), \
                    ", median=", round(med/divScale, 2), ", upper quartile=", round(q3/divScale, 2), ", upper whisker=", round(upperWhisker/divScale, 2))
                print("\t}] coordinates {};")
                print("\t% => max:", round(max(myList)/divScale, 2), ", 99%th:", round(np.percentile(myList, 99)/divScale, 2), ", 95%th:", round(np.percentile(myList, 95)/divScale, 2), ", 90%th:", round(np.percentile(myList, 90)/divScale, 2))
            print("")

            myList = [x for x in DeleteTimes if x != 0]
            for i in range(0, 100+1, 5):
                if i == 100:
                    point = np.percentile(myList, 99)
                    print(99, "percent:", round(point/divScale, 2))

                point = np.percentile(myList, i)
                print(i, "percent:", round(point/divScale, 2))

            #
            # inactivate old account time
            #

            InactivateUpdates = [block_data['InactivateUpdates'] for block_data in data.values()]
            UsedProofUpdtaes = [block_data['UsedProofUpdtaes'] for block_data in data.values()]
            InactivateHashes = [block_data['InactivateHashes'] for block_data in data.values()]
            
            InactivateTimes = [x + y + z for x, y, z in zip(InactivateUpdates, UsedProofUpdtaes, InactivateHashes)]
            blockNums = [int(blockNum) for blockNum in json_keys]

            print("\n\n\nbox plot for Ethane's inactivate time overhead")
            boxPlots = []
            divScale = 1000000 # (10^3: microsecond, 10^6: millisecond, 10^9: second)
            print("divScale:", divScale, "\n")
            for i in range(inactivateCriterion, blockNums[-1], inactivateCriterion):
                myList = [x for x in InactivateTimes[i:i+inactivateCriterion] if x != 0]

                q1 = np.percentile(myList, 25)
                med = median(myList)
                q3 = np.percentile(myList, 75)
                iqr = q3 - q1

                myListWithoutOutliers = [x for x in myList if x >= q1 - 1.5*iqr]
                myListWithoutOutliers.sort()
                lowerWhisker = myListWithoutOutliers[0]

                myListWithoutOutliers = [x for x in myList if x <= q3 + 1.5*iqr]
                myListWithoutOutliers.sort()
                upperWhisker = myListWithoutOutliers[-1]
                
                print("\t% => at round", int(1 + i/inactivateCriterion))
                print("\t\\addplot+ [boxplot prepared={")
                print("\t\tlower whisker=", round(lowerWhisker/divScale, 2), ", lower quartile=", round(q1/divScale, 2), \
                    ", median=", round(med/divScale, 2), ", upper quartile=", round(q3/divScale, 2), ", upper whisker=", round(upperWhisker/divScale, 2))
                print("\t}] coordinates {};")
                print("\t% => max:", round(max(myList)/divScale, 2), ", 99%th:", round(np.percentile(myList, 99)/divScale, 2), ", 95%th:", round(np.percentile(myList, 95)/divScale, 2), ", 90%th:", round(np.percentile(myList, 90)/divScale, 2))
            print("")

            myList = [x for x in InactivateTimes if x != 0]
            for i in range(0, 100+1, 5):
                if i == 100:
                    point = np.percentile(myList, 99)
                    print(99, "percent:", round(point/divScale, 2))
                    
                point = np.percentile(myList, i)
                print(i, "percent:", round(point/divScale, 2))

            print("")
            continue

        elif field_name == "DiskSizeIncPerTx":

            batch_size = 1

            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            DiskSize = [block_data['DiskSize'] for block_data in data.values()]
            blockNums = [index for index, size in enumerate(DiskSize) if size != 0] # block num
            diskSizes = [size for size in DiskSize if size != 0] # disk size

            blockNums = [0] + blockNums
            diskSizes = [0] + diskSizes

            x_values = []
            y_values = []

            for i in range(len(blockNums)-1):
                startBlockNum = blockNums[i]
                endBlockNum = blockNums[i+1]
                diskSizeDiff = diskSizes[i+1] - diskSizes[i]
                txLen = sum(TxLen[startBlockNum+1:endBlockNum+1])

                x_values.append(endBlockNum)
                y_values.append(diskSizeDiff/txLen)


            left_index = bisect.bisect_right(x_values, first_block_to_draw)-1
            right_index = bisect.bisect_right(x_values, last_block_to_draw)

            x_values = x_values[left_index:right_index]
            y_values = y_values[left_index:right_index]

            x_values_list.append(x_values)
            y_values_list.append(y_values)
            label_list.append(sim_mode_name)
        
        elif field_name == "CompareReadTimes":
            PaymentTxExecutes = [block_data['PaymentTxExecutes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            CallTxExecutes = [block_data['CallTxExecutes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            TxExecutes = [paymentExecutes + callExecutes for paymentExecutes, callExecutes in zip(PaymentTxExecutes, CallTxExecutes)]
            if sim_mode_name[:6] == "Ethane":
                sum1 = sum(TxExecutes)
                # actual tx execute time without void reads
                VoidAccountReads = [block_data['VoidAccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                TxExecutes = [te - var for te, var in zip(TxExecutes, VoidAccountReads)]
                sum2 = sum(TxExecutes)

            AccountReads = [block_data['AccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            SnapshotAccountReads = [block_data['SnapshotAccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            if sum(AccountReads) == 0:
                AccountReads = SnapshotAccountReads
            else:
                if sum(SnapshotAccountReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for account")
                    sys.exit()
            ActiveIndexReads = []
            if sim_mode_name[:6] == "Ethane":
                try:
                    ActiveIndexReads = [block_data['ActiveIndexReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                except:
                    ActiveIndexReads = [0]*len(AccountReads)
                AccountReads = [x + y for x, y in zip(AccountReads, ActiveIndexReads)]

                # actual account read time without void reads
                VoidAccountReads = [block_data['VoidAccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                print("account read sum:", sum(AccountReads))
                print("void account read sum:", sum(VoidAccountReads))
                AccountReads = [ar - var for ar, var in zip(AccountReads, VoidAccountReads)]

            StorageReads = [block_data['StorageReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            SnapshotStorageReads = [block_data['SnapshotStorageReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            if sum(StorageReads) == 0:
                StorageReads = SnapshotStorageReads
            else:
                if sum(SnapshotStorageReads) != 0:
                    print("ERROR: this log has both trie read time and snapshot read time for storage")
                    sys.exit()
            TotalReads = [x + y for x, y in zip(AccountReads, StorageReads)]

            PaymentTxLen = [block_data['PaymentTxLen'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            CallTxLen = [block_data['CallTxLen'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            TxLen = [paymentLen + callLen for paymentLen, callLen in zip(PaymentTxLen, CallTxLen)]

            AccountCommits = [block_data['AccountCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            StorageCommits = [block_data['StorageCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            SnapshotCommits = [block_data['SnapshotCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            TrieDBCommits = [block_data['TrieDBCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            DiskCommits = [block_data['DiskCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            TotalCommits = [a + b + c + d + e for a, b, c, d, e in zip(AccountCommits, StorageCommits, SnapshotCommits, TrieDBCommits, DiskCommits)]

            try:
                DeleteUpdates = [block_data['DeleteUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                DeleteHashes = [block_data['DeleteHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                DeleteExecutes = [x + y for x, y in zip(DeleteUpdates, DeleteHashes)]
            except:
                DeleteExecutes = [0]
            
            try:
                InactivateUpdates = [block_data['InactivateUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                UsedProofUpdtaes = [block_data['UsedProofUpdtaes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                InactivateHashes = [block_data['InactivateHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
                InactivateExecutes = [x + y + z for x, y, z in zip(InactivateUpdates, UsedProofUpdtaes, InactivateHashes)]
            except:
                InactivateExecutes = [0]

            BlockExecuteTime = [block_data['BlockExecuteTime'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]

            RestoreUpdates = [block_data['RestoreUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            RestoreCommits = [block_data['RestoreCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            RestoreTrieDBCommits = [block_data['RestoreTrieDBCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            RestoreDiskCommits = [block_data['RestoreDiskCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            TotalRestoreTime = [x + y + z + w for x, y, z, w in zip(RestoreUpdates, RestoreCommits, RestoreTrieDBCommits, RestoreDiskCommits)]

            print("sim mode:", sim_mode_name)
            print("  block range:", first_block_to_draw, "~", last_block_to_draw)

            print("  BlockExecuteTime sum:", sum(BlockExecuteTime))

            print("  PaymentTxLen sum:", sum(PaymentTxLen))
            print("  CallTxLen sum:", sum(CallTxLen))
            print("  TxLen sum:", sum(TxLen))

            print("  PaymentTxExecutes sum:", sum(PaymentTxExecutes))
            print("  CallTxExecutes sum:", sum(CallTxExecutes))
            print("  TxExecutes sum:", sum(TxExecutes))

            print("  AccountReads sum:", sum(AccountReads))
            print("  StorageReads sum:", sum(StorageReads))
            print("  TotalReads sum:", sum(TotalReads))

            print("  AccountCommits sum:", sum(AccountCommits))
            print("  StorageCommits sum:", sum(StorageCommits))
            print("  SnapshotCommits sum:", sum(SnapshotCommits))
            print("  TrieDBCommits sum:", sum(TrieDBCommits))
            print("  DiskCommits sum:", sum(DiskCommits))
            print("  TotalCommits sum:", sum(TotalCommits))

            print("  DeleteExecutes sum:", sum(DeleteExecutes))
            print("  InactivateExecutes sum:", sum(InactivateExecutes))

            print("  ActiveIndexReads(includedInAccountReads) sum:", sum(ActiveIndexReads))

            print("  RestoreUpdates sum:", sum(RestoreUpdates))
            print("  RestoreCommits sum:", sum(RestoreCommits))
            print("  RestoreTrieDBCommits sum:", sum(RestoreTrieDBCommits))
            print("  RestoreDiskCommits sum:", sum(RestoreDiskCommits))
            print("  TotalRestoreTime sum:", sum(TotalRestoreTime))

        elif field_name == "Test":
            print("test")
            pass

        else:
            print("wrong field name:", field_name)
            pass

        # draw lines
        for i in range(len(x_values_list)):
            ax1.plot(x_values_list[i], y_values_list[i], marker='o', markersize=2, label=label_list[i])

            # print values
            print("label:", label_list[i])
            print("x values:", x_values_list[i])
            print("y values:", y_values_list[i])
            print("\n")

        # set axis
        ax1.set_xlabel('Block Number')
        ax1.set_ylabel(field_name)
        ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
    plt.title(field_name + ' (batch size: ' + str(batch_size) + ')')
    plt.legend()

    file_name = field_name + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png'
    plt.savefig(GRAPH_PATH + file_name)

    print("finish analyze, file name:", file_name)
    print("elapsed time:", datetime.now()-startTime)


def graph_stack_graph(first_block_to_draw, last_block_to_draw, datas):

    startTime = datetime.now()

    blockNums = range(first_block_to_draw, last_block_to_draw+1)
    blockExecutes = {}
    y_values_to_stack = {}
    for sim_mode_name, data in datas.items():
        
        # extract fields
        blockExecuteTime = [block_data['BlockExecuteTime'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        PaymentTxExecutes = [block_data['PaymentTxExecutes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        CallTxExecutes = [block_data['CallTxExecutes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        AccountUpdates = [block_data['AccountUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        StorageUpdates = [block_data['StorageUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        AccountHashes = [block_data['AccountHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        StorageHashes = [block_data['StorageHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        AccountCommits = [block_data['AccountCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        StorageCommits = [block_data['StorageCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        SnapshotCommits = [block_data['SnapshotCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        TrieDBCommits = [block_data['TrieDBCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        DiskCommits = [block_data['DiskCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]

        # collect accumulative values
        blockExecutes[sim_mode_name] = np.cumsum(blockExecuteTime)
        y_values_to_stack[sim_mode_name] = [[], []]
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(PaymentTxExecutes))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(CallTxExecutes))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(AccountUpdates))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(StorageUpdates))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(AccountHashes))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(StorageHashes))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(AccountCommits))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(StorageCommits))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(SnapshotCommits))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(TrieDBCommits))
        y_values_to_stack[sim_mode_name][0].append(np.cumsum(DiskCommits))
        
        # collect legends
        y_values_to_stack[sim_mode_name][1].append("PaymentTxExecutes")
        y_values_to_stack[sim_mode_name][1].append("CallTxExecutes")
        y_values_to_stack[sim_mode_name][1].append("AccountUpdates")
        y_values_to_stack[sim_mode_name][1].append("StorageUpdates")
        y_values_to_stack[sim_mode_name][1].append("AccountHashes")
        y_values_to_stack[sim_mode_name][1].append("StorageHashes")
        y_values_to_stack[sim_mode_name][1].append("AccountCommits")
        y_values_to_stack[sim_mode_name][1].append("StorageCommits")
        y_values_to_stack[sim_mode_name][1].append("SnapshotCommits")
        y_values_to_stack[sim_mode_name][1].append("TrieDBCommits")
        y_values_to_stack[sim_mode_name][1].append("DiskCommits")

        if sim_mode_name[:6] == "Ethane":
            DeleteUpdates = [block_data['DeleteUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(DeleteUpdates))
            y_values_to_stack[sim_mode_name][1].append("DeleteUpdates")

            DeleteHashes = [block_data['DeleteHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(DeleteHashes))
            y_values_to_stack[sim_mode_name][1].append("DeleteHashes")

            InactivateUpdates = [block_data['InactivateUpdates'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(InactivateUpdates))
            y_values_to_stack[sim_mode_name][1].append("InactivateUpdates")

            UsedProofUpdtaes = [block_data['UsedProofUpdtaes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(UsedProofUpdtaes))
            y_values_to_stack[sim_mode_name][1].append("UsedProofUpdtaes")

            InactivateHashes = [block_data['InactivateHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(InactivateHashes))
            y_values_to_stack[sim_mode_name][1].append("InactivateHashes")
            
            AccountRestores = [block_data['AccountRestores'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(AccountRestores))
            y_values_to_stack[sim_mode_name][1].append("AccountRestores")
        
        if sim_mode_name[:7] == "Ethanos":
            AccountRestores = [block_data['AccountRestores'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            y_values_to_stack[sim_mode_name][0].append(np.cumsum(AccountRestores))
            y_values_to_stack[sim_mode_name][1].append("AccountRestores")

    # find max y value
    modes = blockExecutes.keys()
    maxExecuteTime = 0
    for mode in modes:
        print("mode:", mode)
        print("blockExecutes[mode]:", blockExecutes[mode])
        if maxExecuteTime < blockExecutes[mode][-1]:
            maxExecuteTime = blockExecutes[mode][-1]

    # draw graph
    for sim_mode_name, _ in datas.items():
        print("draw graph for", sim_mode_name)
        
        fig, ax1 = plt.subplots()

        ax1.set_ylim(top=maxExecuteTime) # set max y value        
        ax1.plot(blockNums, blockExecutes[sim_mode_name], marker='o', markersize=1, label="block execute time")
        ax1.stackplot(blockNums, y_values_to_stack[sim_mode_name][0], labels=y_values_to_stack[sim_mode_name][1], alpha=0.5)

        ax1.set_xlabel('Block Number')
        ax1.set_ylabel('Block execution time analysis')

        ax1.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        
        plt.title('Block execution time analysis')
        plt.legend()

        plt.savefig(GRAPH_PATH + "block_execution_time_analysis_" + sim_mode_name + '_' + str(first_block_to_draw) + "_" + str(last_block_to_draw) + '.png')

        print("elapsed time:", datetime.now()-startTime)

    print("finish analyze")
    print("total elapsed time:", datetime.now()-startTime)


def compare_read_time(first_block_to_draw, last_block_to_draw, datas, window=50000, output_file='compare_read_time.png'):
    
    blockNums = range(first_block_to_draw, last_block_to_draw + 1)
    plt.figure(figsize=(10, 6))

    # block nums to print value (ex: 3M, 4M, ..., 10M)
    target_blocks = list(range(first_block_to_draw, last_block_to_draw+1, window))
    
    for sim_mode_name, data in datas.items():

        AccountReads = [block_data['AccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        StorageReads = [block_data['StorageReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        SnapshotAccountReads = [block_data['SnapshotAccountReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        SnapshotStorageReads = [block_data['SnapshotStorageReads'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]

        readTime = [a + b + c + d for a, b, c, d in zip(AccountReads, StorageReads, SnapshotAccountReads, SnapshotStorageReads)]
        
        # Convert to pandas series for rolling average calculation
        df = pd.Series(readTime, index=blockNums)
        rolling_avg = df.rolling(window=window, min_periods=window).mean()
        
        # Plot the rolling average
        plt.plot(rolling_avg.index, rolling_avg.values, label=f'{sim_mode_name}')

        # print (x, y) values
        print(f"\n[at compare_read_time(): selected points for '{sim_mode_name}'] -> start: {first_block_to_draw}, end: {last_block_to_draw}")
        for blk in target_blocks:
            if blk in rolling_avg.index:
                y = rolling_avg.get(blk, None)
                if pd.notna(y):
                    # print(f"Block {blk}: {y} ns")
                    print(y)
    
    # Graph formatting
    plt.xlabel('Block Number')
    plt.ylabel('Read Time (ns)')
    plt.title(f'Read Time Comparison (MA-{window})')
    plt.legend()
    plt.grid(True)
    
    # Save graph as PNG file
    plt.savefig(GRAPH_PATH + output_file)
    plt.close()
    
    print(f'Graph saved as {output_file}')


def compare_write_time(first_block_to_draw, last_block_to_draw, datas, window=50000, output_file='compare_write_time.png'):

    blockNums = range(first_block_to_draw, last_block_to_draw + 1)
    plt.figure(figsize=(10, 6))

    # block nums to print value (ex: 3M, 4M, ..., 10M)
    target_blocks = list(range(first_block_to_draw, last_block_to_draw+1, window))
    
    for sim_mode_name, data in datas.items():

        AccountCommits = [block_data['AccountCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        StorageCommits = [block_data['StorageCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        SnapshotCommits = [block_data['SnapshotCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        TrieDBCommits = [block_data['TrieDBCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        DiskCommits = [block_data['DiskCommits'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]

        writeTime = [a + b + c + d + e for a, b, c, d, e in zip(AccountCommits, StorageCommits, SnapshotCommits, TrieDBCommits, DiskCommits)]
        
        # Convert to pandas series for rolling average calculation
        df = pd.Series(writeTime, index=blockNums)
        rolling_avg = df.rolling(window=window, min_periods=window).mean()
        
        # Plot the rolling average
        plt.plot(rolling_avg.index, rolling_avg.values, label=f'{sim_mode_name}')

        # print (x, y) values
        print(f"\n[at compare_write_time(): selected points for '{sim_mode_name}'] -> start: {first_block_to_draw}, end: {last_block_to_draw}")
        for blk in target_blocks:
            if blk in rolling_avg.index:
                y = rolling_avg.get(blk, None)
                if pd.notna(y):
                    # print(f"Block {blk}: {y} ns")
                    print(y)
    
    # Graph formatting
    plt.xlabel('Block Number')
    plt.ylabel('Write Time (ns)')
    plt.title(f'Write Time Comparison (MA-{window})')
    plt.legend()
    plt.grid(True)
    
    # Save graph as PNG file
    plt.savefig(GRAPH_PATH + output_file)
    plt.close()
    
    print(f'Graph saved as {output_file}')


def compare_block_execute_time(first_block_to_draw, last_block_to_draw, datas, window=50000, output_file='compare_block_execute_time.png'):

    blockNums = range(first_block_to_draw, last_block_to_draw + 1)
    plt.figure(figsize=(10, 6))
    
    # block nums to print value (ex: 3M, 4M, ..., 10M)
    target_blocks = list(range(first_block_to_draw, last_block_to_draw+1, window))

    for sim_mode_name, data in datas.items():
        # Extract block execution times
        blockExecuteTime = [block_data['BlockExecuteTime'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
        try:
            AccountHashes = [block_data['AccountHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            StorageHashes = [block_data['StorageHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            # modifyHashes = [block_data['ModifyHashes'] for block_data in data.values()][first_block_to_draw:last_block_to_draw+1]
            # blockExecuteTime = [b - m for b, m in zip(blockExecuteTime, modifyHashes)]
            blockExecuteTime = [b - (a + s) for b, a, s in zip(blockExecuteTime, AccountHashes, StorageHashes)]
        except:
            pass
        
        # Convert to pandas series for rolling average calculation
        df = pd.Series(blockExecuteTime, index=blockNums)
        rolling_avg = df.rolling(window=window, min_periods=window).mean()
        
        # Plot the rolling average
        plt.plot(rolling_avg.index, rolling_avg.values, label=f'{sim_mode_name}')
        # plt.plot(rolling_avg.index, rolling_avg.values, marker='o', label=f'{sim_mode_name} (MA-{window})')

        # print (x, y) values
        print(f"\n[at compare_block_execute_time(): selected points for '{sim_mode_name}'] -> start: {first_block_to_draw}, end: {last_block_to_draw}")
        for blk in target_blocks:
            if blk in rolling_avg.index:
                y = rolling_avg.get(blk, None)
                if pd.notna(y):
                    # print(f"Block {blk}: {y} ns")
                    print(y)

    # Graph formatting
    plt.xlabel('Block Number')
    plt.ylabel('Execution Time (ns)')
    plt.title(f'Block Execution Time Comparison (MA-{window})')
    plt.legend()
    plt.grid(True)
    
    # Save graph as PNG file
    plt.savefig(GRAPH_PATH + output_file)
    plt.close()
    
    print(f'Graph saved as {output_file}')


def compare_disk_size(first_block_to_draw, last_block_to_draw, datas, output_file='compare_disk_size.png'):
    startTime = datetime.now()
    
    plt.figure(figsize=(10, 6))

    # block nums to print value (ex: 3M, 4M, ..., 10M)
    target_blocks = list(range(first_block_to_draw, last_block_to_draw+1, 100_000))
    
    for sim_mode_name, data in datas.items():
        # Extract disk size values and filter out zeros
        filtered_data = []
        block_size_map = {}  # 블록 번호 → DiskSize 맵

        for block_key, block_data in data.items():
            block_num = int(block_key)  # Convert key to integer
            if first_block_to_draw <= block_num <= last_block_to_draw:
                disk_size = block_data.get('DiskSize', 0)
                if disk_size > 0:
                    filtered_data.append((block_num, disk_size))
                    block_size_map[block_num] = disk_size
        
        if not filtered_data:
            continue
        
        blockNums, diskSize = zip(*filtered_data)
        
        # Plot non-zero disk size values as a line graph
        plt.plot(blockNums, diskSize, label=f'{sim_mode_name}')

        # print (x, y) values
        print(f"\n[at compare_disk_size(): selected points for '{sim_mode_name}'] -> start: {first_block_to_draw}, end: {last_block_to_draw}")
        for blk in target_blocks:
            if blk in block_size_map:
                # print(f"Block {blk}: {block_size_map[blk]:,} B")
                print(block_size_map[blk])
            # else:
            #     print(f"Block {blk}: (no data or zero)")
    
    # Graph formatting
    plt.xlabel('Block Number')
    plt.ylabel('Disk Size (B)')
    plt.title('Disk Size Comparison')
    plt.legend()
    plt.grid(True)
    
    # Save graph as PNG file
    plt.savefig(GRAPH_PATH + output_file)
    plt.close()
    
    print(f'Graph saved as {output_file}')



if __name__ == "__main__":

    startTime = datetime.now()
    
    # set simulation params
    startBlockNum = 0
    endBlockNum = 10000000
    deleteEpoch = 10
    inactivateEpoch = 10
    inactivateCriterion = 500000
    fromLevel = 0 # how many parent nodes to omit in Merkle proofs
    flushInterval = 1 # block flush interval (default: 1, at every block / but genesis block is always flushed)

    # graph options
    first_block_to_draw = 0
    last_block_to_draw = 10000000
    graph_window_size = 50000

    # collect log data
    datas = {}

    try:
        print("collect Ethereum data")
        sim_blocks_file_name = "evm_simulation_result_Ethereum_" + str(startBlockNum) + "_" + str(endBlockNum) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethereum'] = data 
    except:
        print("  -> no Ethereum data")
        sys.exit()

    try:
        print("collect Ethanos data")
        sim_blocks_file_name = "evm_simulation_result_Ethanos_" + str(startBlockNum) + "_" + str(endBlockNum) + "_" + str(inactivateCriterion) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethanos'] = data 
    except:
        print("  -> no Ethanos data")
        sys.exit()

    try:
        print("collect Ethane data")
        sim_blocks_file_name = "evm_simulation_result_Ethane_" + str(startBlockNum) + "_" + str(endBlockNum) + "_" + str(deleteEpoch) + "_" + str(inactivateEpoch) + "_" + str(inactivateCriterion) + ".json"
        print("  file name:", sim_blocks_file_name)
        with open(LOG_FILE_PATH+sim_blocks_file_name, 'r') as json_file:
            data = json.load(json_file)
            datas['Ethane'] = data 
    except:
        print("  -> no Ethane data")
        sys.exit()


    #
    # draw stack graph for detailed block execution time
    #
    # graph_stack_graph(first_block_to_draw, last_block_to_draw, datas)
    compare_block_execute_time(first_block_to_draw, last_block_to_draw, datas, graph_window_size)
    compare_read_time(first_block_to_draw, last_block_to_draw, datas, graph_window_size)
    compare_write_time(first_block_to_draw, last_block_to_draw, datas, graph_window_size)
    compare_disk_size(first_block_to_draw, last_block_to_draw, datas)


    #
    # select fields to draw graph
    #
    field_names = ["CumumlativeBlockExecuteTime", "AvgBlockExecute", "PaymentTxAvgExecute", "CallTxAvgExecute", "TotalTxAvgExecute", 
                   "AvgReadPerTx", "AvgAccountReadPerTx", "AvgStorageReadPerTx", 
                   "AvgCommitPerTx", "DiskSize", "CompareReadTimes"]
    # field_names = ["EthaneOverheads"]
    for field_name in field_names:
        print("field_name:", field_name)
        draw_graph_to_compare_v2(startBlockNum, endBlockNum, first_block_to_draw, last_block_to_draw, graph_window_size, datas, field_name)
        print("\n\n\n")


    print("total elapsed time:", datetime.now()-startTime)
