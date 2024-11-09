/* Copyright 2012 Yaqiang Wang,
 * yaqiang.wang@gmail.com
 * 
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or (at
 * your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
 * General Public License for more details.
 */
package org.meteoinfo.data.meteodata.micaps;

import org.apache.commons.io.input.BOMInputStream;
import org.meteoinfo.data.meteodata.DataInfo;
import org.meteoinfo.data.meteodata.MeteoDataType;

import java.io.*;
import java.util.RandomAccess;
import java.util.StringTokenizer;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author yaqiang
 */
public class MICAPSDataInfo {
    // <editor-fold desc="Variables">
    // </editor-fold>
    // <editor-fold desc="Constructor">
    // </editor-fold>
    // <editor-fold desc="Get Set Methods">

    /**
     * Get MICAPS data type
     *
     * @param fileName File name
     * @return Data type
     */
    public static MeteoDataType getDataType(String fileName) {
        BufferedReader sr = null;
        MeteoDataType mdType = null;
        try {
            String dataType;
            sr = new BufferedReader(new InputStreamReader(new BOMInputStream(new FileInputStream(fileName)), "gbk"));
            String aLine;
            String[] dataArray;

            aLine = sr.readLine().trim();
//            if (aLine.startsWith("\uFEFF")) {
//                aLine = aLine.substring(1);
//            }
            if (aLine.substring(0, 4).equals("mdfs")) {
                mdType = MeteoDataType.MICAPS_MDFS;
            } else {
                dataArray = aLine.split("\\s+");
                dataType = dataArray[0] + " " + dataArray[1];
                dataType = dataType.trim().toLowerCase();
                if (dataType.equals("diamond 11")) {
                    mdType = MeteoDataType.MICAPS_11;
                } else if (dataType.equals("diamond 13")) {
                    mdType = MeteoDataType.MICAPS_13;
                } else if (dataType.equals("diamond 2")) {
                    mdType = MeteoDataType.MICAPS_2;
                } else if (dataType.equals("diamond 3")) {
                    mdType = MeteoDataType.MICAPS_3;
                } else if (dataType.equals("diamond 4")) {
                    mdType = MeteoDataType.MICAPS_4;
                } else if (dataType.equals("diamond 7")) {
                    mdType = MeteoDataType.MICAPS_7;
                } else if (dataType.contains("iamond 120")) {
                    mdType = MeteoDataType.MICAPS_120;
                } else if (dataType.contains("diamond 131")) {
                    mdType = MeteoDataType.MICAPS_131;
                } else if (dataType.contains("diamond 1")) {
                    mdType = MeteoDataType.MICAPS_1;
                }

                if (mdType == null) {
                    System.out.println(String.format("Unknown MICAPS data file type: %s", dataType));
                }
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(MICAPSDataInfo.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(MICAPSDataInfo.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                if (sr != null) {
                    sr.close();
                }
            } catch (IOException ex) {
                Logger.getLogger(MICAPSDataInfo.class.getName()).log(Level.SEVERE, null, ex);
            }
        }

        return mdType;
    }

    /**
     * Get MICAPS data info
     *
     * @param raf RandomAccessFile object
     * @return Data info
     */
    public static DataInfo getDataInfo(RandomAccessFile raf) {
        DataInfo dataInfo = null;
        try {
            raf.seek(0);
            byte[] bytes = new byte[1000];
            raf.read(bytes);
            String line = new String(bytes).trim();
            if (line.substring(0, 4).equals("mdfs")) {
                dataInfo = new MDFSDataInfo();
            } else {
                StringTokenizer stoker = new StringTokenizer(line);
                if (stoker.countTokens() >= 2) {
                    String dataType = stoker.nextToken() + " " + stoker.nextToken();
                    if (dataType.equals("diamond 11")) {
                        dataInfo = new MICAPS11DataInfo();
                    } else if (dataType.equals("diamond 13")) {
                        dataInfo = new MICAPS13DataInfo();
                    } else if (dataType.contains("iamond 120")) {
                        dataInfo = new MICAPS120DataInfo();
                    } else if (dataType.contains("diamond 131")) {
                        dataInfo = new MICAPS131DataInfo();
                    } else if (dataType.contains("diamond 1")) {
                        dataInfo = new MICAPS1DataInfo();
                    } else if (dataType.equals("diamond 2")) {
                        dataInfo = new MICAPS2DataInfo();
                    } else if (dataType.equals("diamond 3")) {
                        dataInfo = new MICAPS3DataInfo();
                    } else if (dataType.equals("diamond 4")) {
                        dataInfo = new MICAPS4DataInfo();
                    } else if (dataType.equals("diamond 7")) {
                        dataInfo = new MICAPS7DataInfo();
                    }
                }
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(MICAPSDataInfo.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(MICAPSDataInfo.class.getName()).log(Level.SEVERE, null, ex);
        }

        return dataInfo;
    }
    // </editor-fold>
    // <editor-fold desc="Methods">
    // </editor-fold>
}
