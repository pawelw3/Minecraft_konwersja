package com.maciej916.indreb.common.entity.block;

import com.maciej916.indreb.common.interfaces.entity.IProgress;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.common.util.INBTSerializable;

public class BlockEntityProgress implements IProgress, INBTSerializable<CompoundTag> {
   private float progress;
   private float progressMax;
   private boolean changed = false;

   public BlockEntityProgress() {
      this.progress = -1.0F;
      this.progressMax = -1.0F;
   }

   public BlockEntityProgress(CompoundTag nbt) {
      this.deserializeNBT(nbt);
   }

   public BlockEntityProgress(int progress, int progressMax) {
      this.progress = (float)progress;
      this.progressMax = (float)progressMax;
   }

   public void setData(float progress, float progressMax) {
      if (progress != this.progress || progressMax != this.progressMax) {
         this.changed = true;
      }

      this.progress = progress;
      this.progressMax = progressMax;
   }

   public void setProgress(float progress) {
      this.setData(progress, this.progressMax);
   }

   public void incProgress(float progress) {
      this.setData(this.progress + progress, this.progressMax);
   }

   public void decProgress(float progress) {
      this.setData(this.progress - progress, this.progressMax);
   }

   public void setMaxProgress() {
      this.setData(this.progressMax, this.progressMax);
   }

   public void setBoth(float progress) {
      this.setData(progress, progress);
   }

   public void setProgressMax(float progressMax) {
      this.setData(this.progress, progressMax);
   }

   public float getProgress() {
      return this.progress;
   }

   public float getProgressMax() {
      return this.progressMax;
   }

   public boolean changed() {
      return this.changed;
   }

   public void clearChanged() {
      this.changed = false;
   }

   public CompoundTag serializeNBT() {
      CompoundTag nbt = new CompoundTag();
      nbt.m_128350_("progress", this.progress);
      nbt.m_128350_("progressMax", this.progressMax);
      return nbt;
   }

   public void deserializeNBT(CompoundTag nbt) {
      this.progress = (float)nbt.m_128451_("progress");
      this.progressMax = (float)nbt.m_128451_("progressMax");
   }

   @Override
   public String toString() {
      return "Progress{progress=" + this.progress + ", progressMax=" + this.progressMax + "}";
   }
}
